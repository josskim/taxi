@echo off
start cmd /k "cloudflared tunnel run n8n-tunnel"
timeout /t 3
start cmd /k "python C:\taxi\server.py"