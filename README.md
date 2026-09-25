# BroscoTech Mail & Essentials Stack

Complete self-hosted mail infrastructure and services stack running on Docker:
- **docker-mailserver**: IMAP/SMTP mail server with Dovecot & Postfix.
- **SnappyMail**: Modern, fast webmail client.
- **BroscoTech Mail Admin**: Lightweight, sleek web management panel (Resend/Linear UI) for accounts & aliases.
- **PostgreSQL & Redis**: Essentials backend services.
- **Brevo SMTP Relay**: Outbound delivery relay for high deliverability.

## Quick Start
1. Copy `.env.example` to `.env` and fill in your credentials.
2. Run `docker compose up -d`.
3. Start the Mail Manager daemon: `systemctl start mail-manager`.
