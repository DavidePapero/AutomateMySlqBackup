"""Copyright 2025 Infantino Davide

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import json
import subprocess
import os
import datetime
import smtplib
import time
import email
import email.mime
import email.mime.text
import email.mime.multipart
import signal

import post_processor

# typing for python versions < 3.10
import typing

class DiffTime:
    def __init__(self) -> None:
        self.start : datetime.datetime = datetime.datetime.now()

    def reset(self) -> str:
        self.start = datetime.datetime.now()
        return self.get_diff()

    def get_diff(self) -> str:
        end : datetime.datetime = datetime.datetime.now()
        diff : datetime.timedelta = end - self.start
        seconds : int = int(round(diff.total_seconds(), 0))
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def SizeFile(filepath : str) -> str:
    if os.path.isfile(filepath) is False:
        return "0 B"
    size_bytes : int = os.path.getsize(filepath)
    size_unit : str = 'B'
    size : float = float(size_bytes)
    if size_bytes >= 1024:
        size /= 1024.0
        size_unit = 'KB'
    if size_bytes >= 1024 * 1024:
        size /= 1024.0
        size_unit = 'MB'
    if size_bytes >= 1024 * 1024 * 1024:
        size /= 1024.0
        size_unit = 'GB'
    return f"{size:.2f} {size_unit}"

def ReadConfigFile(filepath : str = 'config.json') -> dict:
    config_data : dict = {}
    if os.path.isfile(filepath) is True:
        with open (filepath, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    return config_data

class MySqlDump():
    LOOP : bool = True

    def __init__(self) -> None:
        # detect old python version
        self.OLD_PYTHON : bool = True
        if sys.version_info.minor >= 12:
            self.OLD_PYTHON = False
        self.config : dict = ReadConfigFile()

    def sendMail(self, subject : str, body : str) -> bool:
        mailConfig : dict = self.config.get('send_mail', {})
        destinatari : typing.Union[str, list[str]] = mailConfig.get('to', '')
        mittente : str = mailConfig.get('from', '')
        SMTPHOST : str = mailConfig.get('host', '')
        SMTPPORT : int = mailConfig.get('port',587)
        SMTPUSER : str = mailConfig.get('user', '')
        SMTPPSWD : str = mailConfig.get('pwd' , '')

        if isinstance(destinatari, list):
            destinatari = ', '.join(destinatari)

        msgRoot : email.mime.multipart.MIMEMultipart | email.mime.text.MIMEText = \
            email.mime.text.MIMEText(body, 'plain','utf-8')

        msgRoot['Subject'] = subject
        msgRoot['From'] = mittente
        msgRoot['To']   = destinatari

        to : str | list[str] = destinatari

        contenutoraw : str = msgRoot.as_string()

        print(f"Sending email to: {destinatari} - Subject: {subject}")
        try:
            smtp = smtplib.SMTP(SMTPHOST, SMTPPORT)
            #smtp.set_debuglevel(True)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTPUSER, SMTPPSWD)
            smtp.sendmail(mittente, to, contenutoraw)
            smtp.close()
            # with basic Amazon SES a maximum of 14 emails are sent per second
            time.sleep(1.15)
        except  Exception as why:
            print ( f"sendMail error: {why}" )
            return False
        return True

    def main(self) -> None:

        #today : str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        today : str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

        cmd_bckup : list[str] = ["mysqldump", "-h", "::host::", "--port", "::port::", \
                "-u", "::user::", "--password=::password::", "--log-error=::error_file::", \
                "--set-gtid-purged=OFF", "--single-transaction", "--triggers", "--routines", "--events", \
                "::database::", ">", "::backup_file::"]
        send_mail_config : dict = self.config.get('send_mail', {})
        send_mail_active : bool = len(send_mail_config) > 0
        post_processor_active  : bool = self.config.get('post_processor', False)
        mail_body : str = ''
        all_bck_ok : bool = True
        dt_global : DiffTime = DiffTime()
        dt_local : DiffTime = DiffTime()

        for config in self.config.get('databases', []):
            result_process : bool = True
            error_process : str = ""
            delta_time_bck : str = ""
            delta_time_compress : str = ""
            gzdest : str = ""
            bck_delete : list[str] = []
            size_backup : str = ""
            size_gzbackup : str = ""
            completed_process : typing.Union[subprocess.CompletedProcess, None] = None
            completed_process_old_python :  typing.Union[subprocess.Popen, None] = None

            # some parameters
            hostdb : str = f'{config.get("host", "")}'
            schema : str = f'{config.get("database", "?")}'
            backup_file : str = config.get('backup_file', '')
            error_file : str = config.get('error_file', '')
            backup_path : str = config.get('backup_path', '')
            backup_identifier: str = config.get('name', '')
            backup_number : int = config.get('backup_number', 100)

            # clean up previous files
            if os.path.isfile(backup_file) is True:
                os.remove(backup_file)
            # delete the previous error file
            if os.path.isfile(error_file) is True:
                os.remove(error_file)
            # does the backup subdirectory exist?
            if os.path.isdir(backup_path) is False:
                os.makedirs(backup_path)

            # prepare the backup command
            cmd : list[str] = []
            for param in cmd_bckup:
                for key, value in config.items():
                    placeholder = f"::{key}::"
                    if placeholder in param:
                        if isinstance(value, str) is False:
                            value = str(value)
                        param = param.replace(placeholder, value)
                cmd.append(param)

            dt_local.reset()
            datetime_specific_backup : str = datetime.datetime.now().isoformat(sep='-', timespec='seconds')

            if self.OLD_PYTHON is False:
                print(f"Exec command: {' '.join(cmd)}")
                encoding_platform : str = 'utf-8'
                if sys.platform == 'win32':
                    encoding_platform = 'Windows-1252'
                completed_process = subprocess.run(cmd, shell=True, capture_output=True, encoding=encoding_platform)
                result_process = completed_process.returncode == 0
            else:
                print(f"Exec command: {' '.join(cmd[:-2])}")
                sql_fle = open(cmd[-1], 'w')
                completed_process_old_python = subprocess.Popen(cmd[:-2], stdout=sql_fle)
                completed_process_old_python.wait()
                sql_fle.close()
                #print(sql_cmd)
                result_process = completed_process_old_python.returncode == 0

            delta_time_bck = dt_local.get_diff()
            if result_process is False:
                if self.OLD_PYTHON is False:
                    if completed_process is not None and completed_process.stderr is not None and len(completed_process.stderr) > 1:
                        error_process = completed_process.stderr
                if os.path.isfile(error_file) is True:
                    with open(error_file, 'r', encoding="utf-8") as f:
                        error_process += f.read()
            else:
                size_backup = SizeFile(backup_file)
                # backup file compression
                gzip : list[str] = ['gzip', '-9', backup_file]
                dt_local.reset()
                gzfile : str = f"{backup_file}.gz"
                # remove previous compressed file if exists
                if os.path.isfile(gzfile) is True:
                    print(f"Removing previous compressed file: {gzfile}")
                    os.remove(gzfile)
                print(f"Exec command: {' '.join(gzip)}")
                if self.OLD_PYTHON is False:
                    completed_process = subprocess.run(gzip, shell=True, capture_output=True, encoding='utf-8')
                    result_process = completed_process.returncode == 0
                else:
                    completed_process_old_python = subprocess.Popen(gzip)
                    completed_process_old_python.wait()
                    result_process = completed_process_old_python.returncode == 0
                delta_time_compress = dt_local.get_diff()
                if result_process is True:
                    # move the file
                    gzdest = os.path.join(backup_path, f"{datetime_specific_backup}-{os.path.basename(backup_file)}.gz")
                    os.rename(gzfile, gzdest)
                    size_gzbackup = SizeFile(gzdest)

                    # delete the oldest backups
                    listbckup : list[str] = [filename for filename in os.listdir(backup_path) if filename.endswith(f"{backup_file}.gz")]
                    listbckup.sort()
                    for i in range(len(listbckup) - backup_number):
                        filename : str = listbckup[i]
                        file_path : str = os.path.join(backup_path, filename)
                        try:
                            os.remove(file_path)
                            bck_delete.append(filename)
                        except Exception as e:
                            print(f"Errore cancellazione file {file_path}: {str(e)}")

            # sending report email
            if send_mail_active is True:
                all_bck_ok = all_bck_ok and result_process

                mail_body += "\n----------------------------------------\n\n"
                mail_body += f"Backup report database {backup_identifier} - {'OK' if result_process is True else 'FAILED'}\n"
                mail_body += f"Host: {hostdb}\n"
                mail_body += f"Schema: {schema}\n"
                mail_body += f"File Backup: {gzdest}\n"
                mail_body += f"Backup time: {delta_time_bck}\n"
                if len(delta_time_compress) > 0:
                    mail_body += f"Compression time: {delta_time_compress}\n"
                    mail_body += f"Original size: {size_backup}\n"
                    mail_body += f"Compressed size: {size_gzbackup}\n"
                if len(bck_delete) > 0:
                    mail_body += f"Deleted old backups: {', '.join(bck_delete)}\n"
                if result_process is False:
                    mail_body += f"\nErrors:\n{error_process}\n"

            # post processor
            if post_processor_active is True:
                if len(error_process) == 0:
                    post_processor.postProcessBackupFile(backup_identifier, error_process)

            print(f"Backup database: {config.get('database', '')} - Result: {'OK' if result_process is True else 'FAILED'}")

        if send_mail_active is True:
            delta_time_global = dt_global.get_diff()
            subject = f"{self.config.get('name', 'Backup report')}: {'OK' if all_bck_ok is True else 'FAILED'} - {today}"
            mail_body = f"Global time: {delta_time_global}\n" + mail_body

            self.sendMail(subject, mail_body)

    def Loop(self) -> None:
        global LOOP

        # we are running in docker engine, let's do things right
        signal.signal(signal.SIGINT,  signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        backup_moment : list[tuple[int, int]] = [(13, 10), (20, 0)]
        start : bool = True

        dtLast : datetime.datetime = datetime.datetime.now() - datetime.timedelta(hours = 1)

        for singleconfig in ReadConfigFile().get('databases', []):
            post_processor.StartBackupProcess(singleconfig.get('name', ''))

        while self.LOOP:
            time.sleep(1)
            dtNow : datetime.datetime = datetime.datetime.now()
            if dtNow.weekday() in (5, 6):
                # weekend, skip backup
                continue
            if start or \
                (
                    (dtNow.hour, dtNow.minute) in backup_moment and \
                    ((dtLast.hour != dtNow.hour) or (dtNow.minute != dtLast.minute)) \
                ):
                dtLast = dtNow
                start = False
                self.main()

def signal_handler(signalvalue, frame):
    if MySqlDump.LOOP:
        print ('Shutting Down')
        MySqlDump.LOOP = False
    else:
        print ('Autokill')
        sys.exit(0)

if __name__ == '__main__':
    print(f"Python: {sys.version}")
    print ('Generatore di backup mysql')
    m = MySqlDump()
    m.Loop()
    print('Buonanotte, io qui ho finito')
