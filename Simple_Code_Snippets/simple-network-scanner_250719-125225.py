```python
import socket
import nmap

def scan_network(ip_range):
    """Scans a given IP range and prints the results."""

    nm = nmap.PortScanner()
    nm.scan(hosts=ip_range, arguments='-sn') # -sn for ping scan only

    print("IP Address\tStatus")
    print("------------------------")
    for ip in nm.all_hosts():
        status = nm[ip]['status']['state']
        print(f"{ip}\t\t{status}")


if __name__ == "__main__":
    ip_range = input("Enter the IP range to scan (e.g., 192.168.1.1-254): ")
    scan_network(ip_range)

```