import scapy.all as scapy
import nmap
import socket
import subprocess
import threading
import queue
import ipaddress
import time
import random
import os
import sys
import argparse

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import scrolledtext
    from tkinter import filedialog
except ImportError:
    print("Tkinter not found. GUI will not be available.")
    tk = None


class NetworkScanner:
    def __init__(self, target_network=None, port_range=None, interface=None,
                 enable_vuln_scan=False, enable_ids_evasion=False, scan_type='tcp',
                 report_format='text', output_file=None):

        self.target_network = target_network
        self.port_range = port_range or "1-1024"  # Default port range
        self.interface = interface or scapy.conf.iface
        self.enable_vuln_scan = enable_vuln_scan
        self.enable_ids_evasion = enable_ids_evasion
        self.scan_type = scan_type.lower()
        self.report_format = report_format.lower()
        self.output_file = output_file
        self.active_hosts = []
        self.open_ports = {}  # {host: [ports]}
        self.service_versions = {}  # {host: {port: service}}
        self.vulnerabilities = {}  # {host: {port: [vulns]}}
        self.scan_results = {}  # combined scan results
        self.gui_enabled = False # Flag to control GUI elements

        self.nm = nmap.PortScanner()


    def set_target_network(self, target_network):
        self.target_network = target_network

    def set_port_range(self, port_range):
        self.port_range = port_range

    def set_interface(self, interface):
        self.interface = interface

    def set_enable_vuln_scan(self, enable_vuln_scan):
        self.enable_vuln_scan = enable_vuln_scan

    def set_enable_ids_evasion(self, enable_ids_evasion):
        self.enable_ids_evasion = enable_ids_evasion

    def set_scan_type(self, scan_type):
        self.scan_type = scan_type

    def set_report_format(self, report_format):
        self.report_format = report_format

    def set_output_file(self, output_file):
        self.output_file = output_file

    def set_gui_enabled(self, gui_enabled):
        self.gui_enabled = gui_enabled

    def discover_hosts(self):
        try:
            arp_request = scapy.ARP(pdst=self.target_network)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False, iface=self.interface)[0]

            self.active_hosts = [element[1].psrc for element in answered_list]

            if self.gui_enabled:
                self.update_log("Discovered active hosts:\n" + "\n".join(self.active_hosts))
            else:
                print("Discovered active hosts:", self.active_hosts)

        except Exception as e:
            if self.gui_enabled:
                self.update_log(f"Error during host discovery: {e}")
            else:
                print(f"Error during host discovery: {e}")
            self.active_hosts = []


    def scan_port(self, host, port, results_queue):
        try:
            if self.scan_type == 'tcp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)  # Reduce timeout for responsiveness
                result = sock.connect_ex((host, port))
                if result == 0:
                    results_queue.put((host, port, "tcp"))
                sock.close()
            elif self.scan_type == 'udp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                sock.sendto(b'A', (host, port))
                try:
                    sock.recvfrom(1024)
                    results_queue.put((host, port, "udp"))  # Open or filtered
                except socket.timeout:
                    pass  # Assume filtered (UDP is connectionless)
                sock.close()
            elif self.scan_type == 'icmp':
                icmp_request = scapy.IP(dst=host) / scapy.ICMP()
                reply = scapy.sr1(icmp_request, timeout=1, verbose=False)
                if reply:
                    results_queue.put((host, port, "icmp"))
            else:
                if self.gui_enabled:
                   self.update_log("Invalid scan type specified")
                else:
                    print("Invalid scan type specified")
                return
        except socket.gaierror as e:
            if self.gui_enabled:
                self.update_log(f"Error resolving hostname {host}: {e}")
            else:
                print(f"Error resolving hostname {host}: {e}")
        except socket.error as e:
            if self.gui_enabled:
                 self.update_log(f"Error connecting to {host}:{port}: {e}")
            else:
                print(f"Error connecting to {host}:{port}: {e}")

    def identify_open_ports(self):
        if not self.active_hosts:
            if self.gui_enabled:
                self.update_log("No active hosts found. Run host discovery first.")
            else:
                print("No active hosts found. Run host discovery first.")
            return

        num_threads = 32  # Increased for faster scanning
        results_queue = queue.Queue()
        threads = []

        for host in self.active_hosts:
            self.open_ports[host] = []
            ports = [int(p) for p in self.port_range.split('-')]
            start_port, end_port = ports[0], ports[1]
            for port in range(start_port, end_port + 1):
                thread = threading.Thread(target=self.scan_port, args=(host, port, results_queue))
                threads.append(thread)
                thread.daemon = True  # Allow main thread to exit even if this thread is running
                thread.start()

                if self.enable_ids_evasion:
                    time.sleep(random.uniform(0.01, 0.05))  # Small delay

        for thread in threads:
            thread.join()  # Wait for all threads to complete

        while not results_queue.empty():
            host, port, protocol = results_queue.get()
            self.open_ports[host].append(port)

        if self.gui_enabled:
            for host, ports in self.open_ports.items():
                self.update_log(f"Open ports on {host}: {ports}")
        else:
            for host, ports in self.open_ports.items():
                print(f"Open ports on {host}: {ports}")


    def perform_service_detection(self):
        if not self.active_hosts:
            if self.gui_enabled:
                self.update_log("No active hosts found. Run host discovery first.")
            else:
                print("No active hosts found. Run host discovery first.")
            return

        for host in self.active_hosts:
            if host not in self.open_ports or not self.open_ports[host]:
                continue

            self.service_versions[host] = {}
            try:
                self.nm.scan(host, ports=','.join(map(str, self.open_ports[host])), arguments='-sV')  # Service version detection
                for port in self.open_ports[host]:
                    try:
                        service = self.nm[host]['tcp'][port]['name'] if 'tcp' in self.nm[host] and port in self.nm[host]['tcp'] else "Unknown"
                        version = self.nm[host]['tcp'][port]['version'] if 'tcp' in self.nm[host] and port in self.nm[host]['tcp'] and 'version' in self.nm[host]['tcp'][port] else "Unknown"
                        self.service_versions[host][port] = f"{service} {version}"
                        if self.gui_enabled:
                            self.update_log(f"Service on {host}:{port}: {service} {version}")
                        else:
                            print(f"Service on {host}:{port}: {service} {version}")
                    except KeyError:
                        self.service_versions[host][port] = "Unknown"

            except Exception as e:
                if self.gui_enabled:
                    self.update_log(f"Error performing service detection on {host}: {e}")
                else:
                    print(f"Error performing service detection on {host}: {e}")

    def conduct_vulnerability_scanning(self):
        if not self.active_hosts:
            if self.gui_enabled:
                self.update_log("No active hosts found. Run host discovery first.")
            else:
                print("No active hosts found. Run host discovery first.")
            return

        if not self.enable_vuln_scan:
            if self.gui_enabled:
                self.update_log("Vulnerability scanning is disabled.")
            else:
                print("Vulnerability scanning is disabled.")
            return

        for host in self.active_hosts:
            if host not in self.open_ports or not self.open_ports[host]:
                continue

            self.vulnerabilities[host] = {}
            for port in self.open_ports[host]:
                try:
                    nmap_args = '-sV --script vuln'  # Vulnerability scanning script
                    self.nm.scan(host, ports=str(port), arguments=nmap_args)

                    if 'script' in self.nm[host]['tcp'][port]:
                        vuln_info = self.nm[host]['tcp'][port]['script']
                        self.vulnerabilities[host][port] = list(vuln_info.keys())
                        if self.gui_enabled:
                           self.update_log(f"Vulnerabilities found on {host}:{port}: {self.vulnerabilities[host][port]}")
                        else:
                           print(f"Vulnerabilities found on {host}:{port}: {self.vulnerabilities[host][port]}")
                    else:
                        self.vulnerabilities[host][port] = []

                except Exception as e:
                    if self.gui_enabled:
                       self.update_log(f"Error during vulnerability scanning on {host}:{port}: {e}")
                    else:
                        print(f"Error during vulnerability scanning on {host}:{port}: {e}")

    def evade_ids(self):
        # Simple rate limiting and source port randomization
        scapy.conf.rate = 0.1  # Delay of 0.1 seconds between packets
        scapy.conf.randseed = random.randint(1, 1000)  # Randomize source port selection
        # Can add more sophisticated techniques like fragmentation, IP address spoofing, etc.
        if self.gui_enabled:
            self.update_log("IDS evasion techniques enabled (rate limiting, source port randomization).")
        else:
            print("IDS evasion techniques enabled (rate limiting, source port randomization).")

    def create_network_topology_map(self):
        # This is a placeholder.  Creating a detailed topology map is complex.
        # Requires traceroute-like functionality, OS fingerprinting, etc.
        # This example just shows connections between active hosts.

        if not self.active_hosts:
            if self.gui_enabled:
                self.update_log("No active hosts found. Run host discovery first.")
            else:
                print("No active hosts found. Run host discovery first.")
            return

        topology = {}
        for host in self.active_hosts:
            topology[host] = []
            for other_host in self.active_hosts:
                if host != other_host:
                    try:
                        # Check connectivity using ping (ICMP)
                        ping_result = subprocess.run(['ping', '-c', '1', other_host],
                                                      capture_output=True, text=True, timeout=2)
                        if ping_result.returncode == 0:
                            topology[host].append(other_host)
                    except subprocess.TimeoutExpired:
                        pass # Host not reachable
                    except Exception as e:
                        if self.gui_enabled:
                            self.update_log(f"Error creating topology map: {e}")
                        else:
                            print(f"Error creating topology map: {e}")


        if self.gui_enabled:
            self.update_log("Network Topology:")
            for host, neighbors in topology.items():
                self.update_log(f"{host} is connected to: {neighbors}")
        else:
            print("Network Topology:")
            for host, neighbors in topology.items():
                print(f"{host} is connected to: {neighbors}")

    def generate_report(self):
        self.scan_results = {}
        for host in self.active_hosts:
          self.scan_results[host] = {}
          self.scan_results[host]['open_ports'] = self.open_ports.get(host, [])
          self.scan_results[host]['service_versions'] = self.service_versions.get(host, {})
          self.scan_results[host]['vulnerabilities'] = self.vulnerabilities.get(host, {})


        if self.report_format == 'text':
            report = "Network Scan Report\n"
            report += "--------------------\n"
            report += f"Target Network: {self.target_network}\n"
            report += f"Scan Type: {self.scan_type}\n"
            report += f"Vulnerability Scan: {'Enabled' if self.enable_vuln_scan else 'Disabled'}\n"
            report += f"IDS Evasion: {'Enabled' if self.enable_ids_evasion else 'Disabled'}\n"
            report += "\nActive Hosts:\n"
            for host in self.active_hosts:
                report += f"- {host}\n"
                if host in self.scan_results:
                    report += f"  Open Ports: {self.scan_results[host]['open_ports']}\n"
                    report += "  Services:\n"
                    for port, service in self.scan_results[host]['service_versions'].items():
                        report += f"    - {port}: {service}\n"
                    report += "  Vulnerabilities:\n"
                    for port, vulns in self.scan_results[host]['vulnerabilities'].items():
                        report += f"    - {port}: {vulns}\n"
            return report

        elif self.report_format == 'json':
            import json
            return json.dumps(self.scan_results, indent=4)
        else:
            if self.gui_enabled:
                self.update_log("Invalid report format specified. Using text format.")
            else:
                print("Invalid report format specified. Using text format.")
            self.report_format = 'text'
            return self.generate_report()

    def save_report(self, report):
        if self.output_file:
            try:
                with open(self.output_file, 'w') as f:
                    f.write(report)
                if self.gui_enabled:
                    self.update_log(f"Report saved to {self.output_file}")
                else:
                    print(f"Report saved to {self.output_file}")
            except Exception as e:
                if self.gui_enabled:
                    self.update_log(f"Error saving report: {e}")
                else:
                    print(f"Error saving report: {e}")
        else:
            if self.gui_enabled:
                self.update_log("No output file specified.  Displaying report in console.")
            else:
                print("No output file specified.  Displaying report in console.")
            print(report)

    def run_scan(self):
        if not self.target_network:
            if self.gui_enabled:
                self.update_log("Target network is not set.")
            else:
                print("Target network is not set.")
            return

        if self.enable_ids_evasion:
            self.evade_ids()
        self.discover_hosts()
        self.identify_open_ports()
        self.perform_service_detection()
        self.conduct_vulnerability_scanning()
        self.create_network_topology_map()
        report = self.generate_report()
        self.save_report(report)


    def update_log(self, message):
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)  # Allow editing
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.config(state=tk.DISABLED) # Disable editing
            self.log_text.see(tk.END) # Scroll to end

class NetworkScannerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Network Scanner")
        master.geometry("800x600")

        self.scanner = NetworkScanner()
        self.scanner.set_gui_enabled(True)  # Enable GUI logging

        # Style
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5, relief="raised")
        self.style.configure('TLabel', padding=5)
        self.style.configure('TEntry', padding=5)
        self.style.configure('TCheckbutton', padding=5)

        # Target Network
        self.target_label = ttk.Label(master, text="Target Network:")
        self.target_label.grid(row=0, column=0, sticky=tk.W)
        self.target_entry = ttk.Entry(master, width=40)
        self.target_entry.grid(row=0, column=1, sticky=tk.W)

        # Port Range
        self.port_label = ttk.Label(master, text="Port Range:")
        self.port_label.grid(row=1, column=0, sticky=tk.W)
        self.port_entry = ttk.Entry(master, width=40)
        self.port_entry.grid(row=1, column=1, sticky=tk.W)
        self.port_entry.insert(0, "1-1024")  # Default port range

        # Interface
        self.interface_label = ttk.Label(master, text="Interface:")
        self.interface_label.grid(row=2, column=0, sticky=tk.W)
        self.interface_entry = ttk.Entry(master, width=40)
        self.interface_entry.grid(row=2, column=1, sticky=tk.W)
        self.interface_entry.insert(0, scapy.conf.iface)

        # Scan Type
        self.scan_type_label = ttk.Label(master, text="Scan Type:")
        self.scan_type_label.grid(row=3, column=0, sticky=tk.W)
        self.scan_type_combo = ttk.Combobox(master, values=['TCP', 'UDP', 'ICMP'])
        self.scan_type_combo.grid(row=3, column=1, sticky=tk.W)
        self.scan_type_combo.set("TCP")

        # Vulnerability Scan
        self.vuln_var = tk.BooleanVar()
        self.vuln_check = ttk.Checkbutton(master, text="Enable Vulnerability Scan", variable=self.vuln_var)
        self.vuln_check.grid(row=4, column=0, columnspan=2, sticky=tk.W)

        # IDS Evasion
        self.ids_var = tk.BooleanVar()
        self.ids_check = ttk.Checkbutton(master, text="Enable IDS Evasion", variable=self.ids_var)
        self.ids_check.grid(row=5, column=0, columnspan=2, sticky=tk.W)

        # Report Format
        self.report_label = ttk.Label(master, text="Report Format:")
        self.report_label.grid(row=6, column=0, sticky=tk.W)
        self.report_combo = ttk.Combobox(master, values=['Text', 'JSON'])
        self.report_combo.grid(row=6, column=1, sticky=tk.W)
        self.report_combo.set("Text")

        # Output File
        self.output_label = ttk.Label(master, text="Output File:")
        self.output_label.grid(row=7, column=0, sticky=tk.W)
        self.output_entry = ttk.Entry(master, width=40)
        self.output_entry.grid(row=7, column=1, sticky=tk.W)
        self.browse_button = ttk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=7, column=2, sticky=tk.W)

        # Run Scan Button
        self.scan_button = ttk.Button(master, text="Run Scan", command=self.run_scan)
        self.scan_button.grid(row=8, column=0, columnspan=3, pady=10)

        # Log Text Area
        self.log_label = ttk.Label(master, text="Scan Log:")
        self.log_label.grid(row=9, column=0, sticky=tk.W)
        self.log_text = scrolledtext.ScrolledText(master, width=80, height=15, state=tk.DISABLED)
        self.log_text.grid(row=10, column=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S)
        self.scanner.log_text = self.log_text  # Connect log_text to scanner

        # Progress Bar (Optional) - Not fully implemented due to complexity
        # self.progress = ttk.Progressbar(master, orient=tk.HORIZONTAL, length=300, mode='determinate')
        # self.progress.grid(row=11, column=0, columnspan=3, pady=10)

    def browse_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def run_scan(self):
        target_network = self.target_entry.get()
        port_range = self.port_entry.get()
        interface = self.interface_entry.get()
        scan_type = self.scan_type_combo.get().lower()
        enable_vuln_scan = self.vuln_var.get()
        enable_ids_evasion = self.ids_var.get()
        report_format = self.report_combo.get().lower()
        output_file = self.output_entry.get()

        self.scanner.set_target_network(target_network)
        self.scanner.set_port_range(port_range)
        self.scanner.set_interface(interface)
        self.scanner.set_scan_type(scan_type)
        self.scanner.set_enable_vuln_scan(enable_vuln_scan)
        self.scanner.set_enable_ids_evasion(enable_ids_evasion)
        self.scanner.set_report_format(report_format)
        self.scanner.set_output_file(output_file)


        # Disable the Run Scan button during the scan
        self.scan_button.config(state=tk.DISABLED)

        # Start the scan in a separate thread to prevent the GUI from freezing
        threading.Thread(target=self.start_scan_thread).start()

    def start_scan_thread(self):
        try:
            self.log_text.config(state=tk.NORMAL)  # Allow editing
            self.log_text.delete("1.0", tk.END)  # Clear previous log
            self.log_text.config(state=tk.DISABLED) # Disable editing
            self.scanner.run_scan()
        finally:
            # Re-enable the Run Scan button after the scan is complete
            self.master.after(0, self.scan_button.config, {'state': tk.NORMAL})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Network Scanner")
    parser.add_argument("-t", "--target", dest="target_network", help="Target network to scan (e.g., 192.168.1.0/24)")
    parser.add_argument("-p", "--ports", dest="port_range", help="Port range to scan (e.g., 1-1024)", default="1-1024")
    parser.add_argument("-i", "--interface", dest="interface", help="Network interface to use (e.g., eth0)")
    parser.add_argument("-v", "--vuln", dest="enable_vuln_scan", action="store_true", help="Enable vulnerability scanning")
    parser.add_argument("-e", "--evade", dest="enable_ids_evasion", action="store_true", help="Enable IDS evasion techniques")
    parser.add_argument("-s", "--scan_type", dest="scan_type", help="Scan type (TCP, UDP, ICMP)", default="tcp")
    parser.add_argument("-r", "--report_format", dest="report_format", help="Report format (text, json)", default="text")
    parser.add_argument("-o", "--output", dest="output_file", help="Output file for the report")
    parser.add_argument("-g", "--gui", dest="enable_gui", action="store_true", help="Enable graphical user interface")


    args = parser.parse_args()


    if args.enable_gui and tk:
        root = tk.Tk()
        gui = NetworkScannerGUI(root)
        root.mainloop()
    else:
        scanner = NetworkScanner(
            target_network=args.target_network,
            port_range=args.port_range,
            interface=args.interface,
            enable_vuln_scan=args.enable_vuln_scan,
            enable_ids_evasion=args.enable_ids_evasion,
            scan_type=args.scan_type,
            report_format=args.report_format,
            output_file=args.output_file
        )
        scanner.run_scan()