# madras-medley


Startup on local command - 

IPADDRESS=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
hugo server --bind $IPADDRESS --baseURL=http://$IPADDRESS
