FROM centos:latest
ENV container docker
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]
RUN sed -i -e "s|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-*
RUN sed -i -e "s|mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-*
RUN yum install -y gcc python3.8 wget
RUN cd /home
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
RUN yum install -y ./google-chrome-stable_current_*.rpm
COPY telegram_bot.py /home/before_it_melts_telegram_bot.py
# main.py, models 패키지 추가 필요
COPY melt_check.py /home/melt_check.py
COPY requirements.txt /home/requirements.txt
COPY docker_config.py /home/config.py
RUN pip3 install -r /home/requirements.txt
COPY dockerrun.sh /usr/local/bin/dockerrun.sh
RUN chmod +x /usr/local/bin/dockerrun.sh
RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
CMD ["dockerrun.sh"]