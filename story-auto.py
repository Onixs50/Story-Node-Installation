import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich import print
from alive_progress import alive_bar

console = Console()

def run_command(command, show_output=True):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if show_output:
        if output:
            console.log(f"[green]{output.decode('utf-8')}[/green]")
        if error:
            console.log(f"[red]{error.decode('utf-8')}[/red]")

def install_dependencies():
    console.rule("[bold blue]Step 1: Installing Dependencies[/bold blue]")
    run_command("sudo apt update && sudo apt upgrade -y")
    run_command("sudo apt install curl tar wget clang pkg-config libssl-dev jq build-essential bsdmainutils git make ncdu gcc git jq chrony liblz4-tool -y")

def install_go():
    console.rule("[bold blue]Step 2: Installing Go[/bold blue]")
    ver = "1.21.6"
    run_command(f"wget https://golang.org/dl/go{ver}.linux-amd64.tar.gz")
    run_command("sudo rm -rf /usr/local/go")
    run_command(f"sudo tar -C /usr/local -xzf go{ver}.linux-amd64.tar.gz")
    run_command(f"rm go{ver}.linux-amd64.tar.gz")
    run_command('echo "export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin" >> $HOME/.bash_profile')
    run_command("source $HOME/.bash_profile")
    run_command("go version")

def install_story_and_geth():
    console.rule("[bold blue]Step 3: Installing Story Geth[/bold blue]")
    run_command("cd $HOME && mkdir -p go/bin/")
    
    # Using a progress bar for downloads
    with alive_bar(2, title="Downloading Story Geth") as bar:
        run_command("wget https://story-geth-binaries.s3.us-west-1.amazonaws.com/geth-public/geth-linux-amd64-0.9.2-ea9f0d2.tar.gz", show_output=False)
        bar()
        run_command("wget https://story-geth-binaries.s3.us-west-1.amazonaws.com/story-public/story-linux-amd64-0.9.11-2a25df1.tar.gz", show_output=False)
        bar()
    
    run_command("tar -xvf geth-linux-amd64-0.9.2-ea9f0d2.tar.gz")
    run_command("tar -xvf story-linux-amd64-0.9.11-2a25df1.tar.gz")
    run_command("mv ~/geth-linux-amd64-0.9.2-ea9f0d2/geth ~/go/bin/story-geth")
    run_command("mv ~/story-linux-amd64-0.9.11-2a25df1/story ~/go/bin/")
    run_command("mkdir -p ~/.story/story")
    run_command("mkdir -p ~/.story/geth")

def setup_validator(node_name):
    console.rule(f"[bold blue]Step 4: Initializing Story Node for {node_name}[/bold blue]")
    run_command("story version")
    run_command(f"story init --network iliad --moniker '{node_name}'")
    run_command('wget -O $HOME/.story/story/config/addrbook.json "https://raw.githubusercontent.com/111STAVR111/props/main/Story/addrbook.json"')

def configure_services():
    console.rule("[bold blue]Step 5: Configuring Services[/bold blue]")
    service_story_geth = '''[Unit]
Description=Story Geth Client
After=network.target

[Service]
User=$USER
ExecStart=$HOME/go/bin/story-geth --iliad --syncmode full
Restart=on-failure
RestartSec=3
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
'''

    service_story = '''[Unit]
Description=Story Consensus Client
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/.story/story
ExecStart=$HOME/go/bin/story run
Restart=on-failure
RestartSec=3
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/story-geth.service', 'w') as f:
        f.write(service_story_geth)
    
    with open('/etc/systemd/system/story.service', 'w') as f:
        f.write(service_story)
    
    run_command("sudo systemctl daemon-reload")
    run_command("sudo systemctl enable story-geth")
    run_command("sudo systemctl enable story")

def restart_services():
    console.rule("[bold blue]Step 6: Restarting Services[/bold blue]")
    run_command("sudo systemctl restart story-geth && sudo journalctl -fu story-geth -o cat")
    run_command("sudo systemctl restart story && sudo journalctl -fu story -o cat")

def export_private_key():
    console.rule("[bold blue]Step 7: Exporting Validator Private Key[/bold blue]")
    run_command("story validator export --export-evm-key")
    console.print("[bold yellow]Copy the private key shown above![/bold yellow]")
    console.print("[bold yellow]Use the following command to create your validator:[/bold yellow]")
    console.print('[bold cyan]story validator create --stake 1000000000000000000 --private-key "your_private_key"[/bold cyan]')
    console.print("[bold yellow]Make sure you have enough funds![/bold yellow]")

def main():
    console.print("[bold magenta]Coded by Onixia[/bold magenta]", style="bold yellow")
    node_name = Prompt.ask("[bold blue]Enter your node name[/bold blue]")
    
    install_dependencies()
    install_go()
    install_story_and_geth()
    setup_validator(node_name)
    configure_services()
    restart_services()
    export_private_key()

if __name__ == "__main__":
    main()
