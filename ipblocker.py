import os
import re
import time
import sqlite3
import subprocess

# class IpBlicker
class IpBlocker:
    def __init__(self, dbfile):
        # check if dbfile exists
        if not os.path.isfile(dbfile):
            self.dbfile = dbfile
            self.conn = sqlite3.connect(dbfile)
            self.cur = self.conn.cursor()
            self.cur.execute('CREATE TABLE IF NOT EXISTS ipblocker (id INTEGER PRIMARY KEY, ip TEXT, time INTEGER, count INTEGER)')
            self.conn.commit()
        else:
            self.dbfile = dbfile
            self.conn = sqlite3.connect(dbfile)
            self.cur = self.conn.cursor()
            # load all ips from db
            for line in self.selectall():
                self.blockip(line[1])

    # insert ip into db
    def insert(self, ip, time, count):
        self.cur.execute('INSERT INTO ipblocker (ip, time, count) VALUES (?, ?, ?)', (ip, time, count))
        self.conn.commit()

    # update row for ip
    def update(self, ip, time, count):
        self.cur.execute('UPDATE ipblocker SET time=?, count=? WHERE ip=?', (time, count, ip))
        self.conn.commit()

    # return information for ip
    def select(self, ip):
        self.cur.execute('SELECT * FROM ipblocker WHERE ip=?', (ip,))
        return self.cur.fetchone()

    # return all ips
    def selectall(self):
        self.cur.execute('SELECT * FROM ipblocker')
        return self.cur.fetchall()

    # delete one ip
    def delete(self, ip):
        self.cur.execute('DELETE FROM ipblocker WHERE ip=?', (ip,))
        self.conn.commit()

    # close db
    def close(self):
        self.conn.close()
    
    # block ip
    def blockip(self, ip):
        subprocess.call(['iptables', '-I', 'INPUT', '-s', ip, '-j', 'DROP'])

    # unblock ip
    def unblockip(self, ip):
        subprocess.call(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'])

    # tail -f log
    def tailf(self, logfile):
        with open(logfile, 'r') as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line

    # parse log
    def parse(self, line):
        pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
        match = pattern.search(line)
        if match:
            ip = match.group(1)
            return ip
        else:
            return None
    

if __name__ == '__main__':
    ipstounlock = [
        'localhost'
    ]
    
    # init ipblocker
    ipblocker = IpBlocker('ipblocker.db')
    # unblock some ips
    for ip in ipstounlock:
        ipblocker.unblockip(ip)
        ipblocker.delete(ip)
    # tail -f log
    for line in ipblocker.tailf('/var/log/secure'):
        # parse log
        ip = ipblocker.parse(line)
        if ip:
            # check if ip exists
            if ipblocker.select(ip):
                # update ip
                ipblocker.update(ip, int(time.time()), ipblocker.select(ip)[3] + 1)
                # block ip
                if ipblocker.select(ip)[3] >= 10:
                    ipblocker.blockip(ip)
            else:
                # insert ip
                ipblocker.insert(ip, int(time.time()), 1)

    # close db
    ipblocker.close()
