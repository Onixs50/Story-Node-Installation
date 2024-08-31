# Story-Node-Installation
## Preparing the server
```bash 
sudo apt update && sudo apt upgrade -y
sudo apt install curl tar wget clang pkg-config libssl-dev jq build-essential bsdmainutils git make ncdu gcc git jq chrony liblz4-tool -y
```
**GO 1.21.6**
```bash 
ver="1.21.6"
wget "https://golang.org/dl/go$ver.linux-amd64.tar.gz"
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "go$ver.linux-amd64.tar.gz"
rm "go$ver.linux-amd64.tar.gz"
echo "export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin" >> $HOME/.bash_profile
source $HOME/.bash_profile
go version
```
**Build**
```bash
cd $HOME && mkdir -p go/bin/
```
```bash
wget https://story-geth-binaries.s3.us-west-1.amazonaws.com/geth-public/geth-linux-amd64-0.9.2-ea9f0d2.tar.gz
wget https://story-geth-binaries.s3.us-west-1.amazonaws.com/story-public/story-linux-amd64-0.9.11-2a25df1.tar.gz
tar -xvf geth-linux-amd64-0.9.2-ea9f0d2.tar.gz
tar -xvf story-linux-amd64-0.9.11-2a25df1.tar.gz
```
```bash
mv ~/geth-linux-amd64-0.9.2-ea9f0d2/geth ~/go/bin/story-geth
mv ~/story-linux-amd64-0.9.11-2a25df1/story ~/go/bin/
```
```bash
mkdir -p ~/.story/story
mkdir -p ~/.story/geth
```

**chek version**
```python
story version
```

![image](https://github.com/user-attachments/assets/76065482-562a-41a8-8d05-1fed0b7c83a0)

## Start

>>change your moniker name

```bash
story init --network iliad --moniker "onixia_node"
```
```bash
wget -O $HOME/.story/story/config/addrbook.json "https://raw.githubusercontent.com/111STAVR111/props/main/Story/addrbook.json"
```
## Create a service file
```bash
sudo tee /etc/systemd/system/story-geth.service > /dev/null <<EOF
[Unit]
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
EOF

sudo tee /etc/systemd/system/story.service > /dev/null <<EOF
[Unit]
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
EOF
```
## peers
```bash 
PEERS="cbaa226e66502b6b032f5e648d4d754f26bf9ca6@65.109.84.22:47656,d0e9bd78ffbd7584bdb5d47a5cc29302de9a2a9a@158.220.81.176:50992,500208ae8b0b20f8d74c16d14ed5f26492825a2a@37.27.91.228:26656,be00a9c3fd1d33e52cc89595c62b1b714cdf1f32@141.98.217.86:26656,2a8119813fd2300157154649bd946a458cbbe7e4@84.247.189.90:26656,aa6333bc781ba361e34770385e97a64ab10a4f8f@5.75.178.20:26656,e63e9aa76ab70b57f47c6c98e9d229b625ad3c37@185.185.82.170:26656,750a308126bd6ce31f2e55370f4eddc6fbb096f1@212.90.121.116:26656,9da641aec497be3ab6a3e8a2d2d5c7d38f773c31@194.163.172.171:26656,20a08afa877675aa66a65ee1ad36d5db4ae9dc5e@193.233.164.18:26656"
sed -i.bak -e "s/^persistent_peers *=.*/persistent_peers = \"$PEERS\"/" $HOME/.story/story/config/config.toml
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable story-geth
sudo systemctl enable story
sudo systemctl restart story-geth && sudo journalctl -fu story-geth -o cat
sudo systemctl restart story && sudo journalctl -fu story -o cat
```
## Wallet
```bash
story validator export --export-evm-key
```
## Create validator

```bash
story validator create --stake 1000000000000000000 --private-key "your_private_key"
```
## Check the sync status:
```bash
curl -s http://localhost:26657/status | jq .result.sync_info
```
