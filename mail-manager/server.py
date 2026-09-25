#!/usr/bin/env python3
import http.server
import json
import os
import re
import secrets
import subprocess
import urllib.parse
from http.cookies import SimpleCookie

PORT = 8085
ADMIN_PASS = os.environ.get("MAIL_ADMIN_PASS", "AdminBrosco2026!@#")
SESSIONS = set()

HTML_PAGE = """<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BroscoTech Mail Infrastructure • Admin</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    :root {
      --bg: #000000;
      --surface: #0a0b0e;
      --surface-elevated: #111318;
      --surface-border: rgba(255, 255, 255, 0.08);
      --surface-border-hover: rgba(255, 255, 255, 0.16);
      --frost-border: rgba(214, 235, 253, 0.14);
      --text-primary: #f0f3f6;
      --text-secondary: #9499a3;
      --text-muted: #5c616d;
      --brand-emerald: #10b981;
      --brand-emerald-glow: rgba(16, 185, 129, 0.15);
      --brand-accent: #3b82f6;
      --danger: #ef4444;
      --font-sans: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    body {
      background-color: var(--bg);
      color: var(--text-primary);
      font-family: var(--font-sans);
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      background-image: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(16, 185, 129, 0.08), transparent 70%),
        radial-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px);
      background-size: 100% 100%, 28px 28px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }

    /* Layout */
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
    }

    /* Header */
    header {
      border-bottom: 1px solid var(--surface-border);
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      position: sticky;
      top: 0;
      z-index: 40;
    }

    .header-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 72px;
    }

    .brand-wrap {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-logo {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      background: linear-gradient(135deg, #18202c 0%, #0d121a 100%);
      border: 1px solid var(--frost-border);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #34d399;
      box-shadow: 0 4px 16px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
    }

    .brand-info h1 {
      font-size: 15px;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .live-tag {
      font-size: 11px;
      font-weight: 500;
      color: #34d399;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      padding: 2px 8px;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 9999px;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }

    .brand-sub {
      font-size: 12px;
      color: var(--text-muted);
      font-family: var(--font-mono);
      margin-top: 1px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    /* Buttons */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-family: var(--font-sans);
      font-size: 13px;
      font-weight: 500;
      padding: 8px 16px;
      border-radius: 9999px;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s ease;
      border: none;
      outline: none;
    }

    .btn-primary {
      background: #ffffff;
      color: #000000;
      font-weight: 600;
      box-shadow: 0 2px 10px rgba(255, 255, 255, 0.15);
    }
    .btn-primary:hover {
      background: #e8e8e8;
      transform: translateY(-1px);
    }

    .btn-ghost {
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-primary);
      border: 1px solid var(--surface-border);
    }
    .btn-ghost:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: var(--surface-border-hover);
    }

    .btn-danger-ghost {
      background: transparent;
      color: var(--text-muted);
      border: 1px solid transparent;
      padding: 6px 12px;
      border-radius: 8px;
    }
    .btn-danger-ghost:hover {
      color: var(--danger);
      background: rgba(239, 68, 68, 0.08);
      border-color: rgba(239, 68, 68, 0.2);
    }

    .btn-action-small {
      font-size: 12px;
      padding: 6px 12px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-secondary);
      border: 1px solid var(--surface-border);
    }
    .btn-action-small:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-primary);
      border-color: var(--surface-border-hover);
    }

    /* Grid Overview Cards */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin: 32px 0;
    }

    .metric-card {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 16px;
      padding: 20px;
      position: relative;
      overflow: hidden;
      transition: border-color 0.2s;
    }
    .metric-card:hover {
      border-color: var(--surface-border-hover);
    }

    .metric-card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .metric-card-value {
      font-size: 26px;
      font-weight: 700;
      color: #ffffff;
      margin-top: 10px;
      letter-spacing: -0.03em;
    }

    .metric-card-desc {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
      font-family: var(--font-mono);
    }

    /* Toolbar */
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .tabs-nav {
      display: flex;
      background: var(--surface);
      border: 1px solid var(--surface-border);
      padding: 4px;
      border-radius: 9999px;
      gap: 4px;
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-family: var(--font-sans);
      font-size: 13px;
      font-weight: 500;
      padding: 6px 16px;
      border-radius: 9999px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s;
    }
    .tab-btn.active {
      background: var(--surface-elevated);
      color: #ffffff;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 2px 6px rgba(0,0,0,0.4);
    }

    .search-box {
      position: relative;
      min-width: 240px;
    }

    .search-input {
      width: 100%;
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 9999px;
      padding: 8px 16px 8px 36px;
      color: #ffffff;
      font-family: var(--font-sans);
      font-size: 13px;
      outline: none;
      transition: border-color 0.15s;
    }
    .search-input:focus {
      border-color: rgba(255, 255, 255, 0.3);
    }
    .search-icon {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }

    /* Table / Card List */
    .table-container {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 16px;
      overflow: hidden;
      margin-bottom: 40px;
    }

    .mail-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      border-bottom: 1px solid var(--surface-border);
      transition: background 0.15s;
    }
    .mail-row:last-child {
      border-bottom: none;
    }
    .mail-row:hover {
      background: rgba(255, 255, 255, 0.015);
    }

    .account-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.01));
      border: 1px solid var(--surface-border);
      color: #34d399;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 700;
      font-family: var(--font-mono);
    }

    .account-details .email-name {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      font-family: var(--font-mono);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .account-details .email-meta {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .account-middle {
      display: flex;
      align-items: center;
      gap: 24px;
    }

    .stat-pill {
      font-size: 12px;
      color: var(--text-secondary);
      font-family: var(--font-mono);
      background: rgba(255, 255, 255, 0.03);
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .account-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* Modal Backdrop */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 50;
      padding: 20px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }
    .modal-backdrop.show {
      opacity: 1;
      pointer-events: auto;
    }

    .modal-dialog {
      background: #0d0e12;
      border: 1px solid var(--surface-border-hover);
      border-radius: 20px;
      width: 100%;
      max-width: 460px;
      padding: 28px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.1);
      transform: translateY(8px) scale(0.98);
      transition: transform 0.2s ease;
    }
    .modal-backdrop.show .modal-dialog {
      transform: translateY(0) scale(1);
    }

    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
    }

    .modal-title {
      font-size: 16px;
      font-weight: 600;
      color: #ffffff;
      letter-spacing: -0.01em;
    }

    .close-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 4px;
      border-radius: 6px;
      transition: color 0.15s;
    }
    .close-btn:hover {
      color: #ffffff;
    }

    .form-group {
      margin-bottom: 18px;
    }

    .form-label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }

    .input-wrapper {
      position: relative;
    }

    .input-text {
      width: 100%;
      background: #050608;
      border: 1px solid var(--surface-border);
      border-radius: 10px;
      padding: 10px 14px;
      color: #ffffff;
      font-family: var(--font-mono);
      font-size: 13px;
      outline: none;
      transition: border-color 0.15s;
    }
    .input-text:focus {
      border-color: rgba(255, 255, 255, 0.4);
    }

    .input-group {
      display: flex;
      border: 1px solid var(--surface-border);
      border-radius: 10px;
      overflow: hidden;
      background: #050608;
    }
    .input-group input {
      flex: 1;
      background: transparent;
      border: none;
      padding: 10px 14px;
      color: #ffffff;
      font-family: var(--font-mono);
      font-size: 13px;
      outline: none;
    }
    .input-group-addon {
      background: rgba(255, 255, 255, 0.04);
      border-left: 1px solid var(--surface-border);
      color: var(--text-muted);
      font-family: var(--font-mono);
      font-size: 12px;
      padding: 0 14px;
      display: flex;
      align-items: center;
    }

    .gen-pass-btn {
      background: transparent;
      border: none;
      color: #34d399;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      margin-left: auto;
    }
    .gen-pass-btn:hover {
      text-decoration: underline;
    }

    /* Toast */
    #toast-box {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 60;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .toast {
      background: #0f1117;
      border: 1px solid var(--frost-border);
      border-radius: 12px;
      padding: 12px 18px;
      font-size: 13px;
      font-weight: 500;
      color: #ffffff;
      box-shadow: 0 8px 30px rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      gap: 10px;
      animation: slideUp 0.2s ease forwards;
    }

    @keyframes slideUp {
      from { transform: translateY(12px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    @media (max-width: 860px) {
      .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
      }
      .mail-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 14px;
      }
      .account-middle, .account-actions {
        width: 100%;
        justify-content: space-between;
      }
    }
    @media (max-width: 520px) {
      .metrics-grid {
        grid-template-columns: 1fr;
      }
      .toolbar {
        flex-direction: column;
        align-items: stretch;
      }
    }
  </style>
</head>
<body>

  <div id="toast-box"></div>

  <!-- Login Modal -->
  <div id="login-modal" class="modal-backdrop">
    <div class="modal-dialog">
      <div style="text-align: center; margin-bottom: 24px;">
        <div style="width: 44px; height: 44px; border-radius: 12px; background: #131720; border: 1px solid var(--frost-border); margin: 0 auto 14px; display: flex; align-items: center; justify-content: center; color: #34d399;">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff;">BroscoTech Mail Admin</h2>
        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Insira a senha mestra para gerenciar o cluster</p>
      </div>

      <form onsubmit="handleLogin(event)">
        <div class="form-group">
          <label class="form-label">Senha Mestra</label>
          <input type="password" id="admin-pass" required placeholder="••••••••••••" class="input-text" style="text-align: center; letter-spacing: 2px;">
        </div>
        <div id="login-error" style="color: var(--danger); font-size: 12px; text-align: center; margin-bottom: 12px; display: none;">Senha incorreta.</div>
        <button type="submit" class="btn btn-primary" style="width: 100%; padding: 12px;">Entrar no Painel</button>
      </form>
    </div>
  </div>

  <!-- App Header -->
  <header>
    <div class="container header-inner">
      <div class="brand-wrap">
        <div class="brand-logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
        </div>
        <div class="brand-info">
          <h1>
            BroscoTech Mail Admin
            <span class="live-tag"><span class="live-dot"></span> Cluster Online</span>
          </h1>
          <div class="brand-sub">mailadmin.broscotech.com.br</div>
        </div>
      </div>

      <div class="header-actions">
        <a href="https://mail.broscotech.com.br" target="_blank" class="btn btn-ghost">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2 2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          <span>Abrir Webmail</span>
        </a>
        <button onclick="logout()" class="btn btn-ghost" style="padding: 8px 12px;" title="Encerrar Sessão">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="container">

    <!-- Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-card-top">
          <span>Caixas de E-mail</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="metric-card-value" id="stat-accounts">0</div>
        <div class="metric-card-desc">@broscotech.com.br</div>
      </div>

      <div class="metric-card">
        <div class="metric-card-top">
          <span>Aliases & Encaminhamentos</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        </div>
        <div class="metric-card-value" id="stat-aliases">0</div>
        <div class="metric-card-desc">Redirecionamentos ativos</div>
      </div>

      <div class="metric-card">
        <div class="metric-card-top">
          <span>Servidor IMAP</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
        </div>
        <div class="metric-card-value" style="font-size: 20px; color: #34d399; margin-top: 14px;">Dovecot IMAPS</div>
        <div class="metric-card-desc">Porta 993 (SSL Ativo)</div>
      </div>

      <div class="metric-card">
        <div class="metric-card-top">
          <span>Relay de Envio</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </div>
        <div class="metric-card-value" style="font-size: 20px; color: #60a5fa; margin-top: 14px;">Brevo SMTP</div>
        <div class="metric-card-desc">Porta 587 (STARTTLS)</div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="tabs-nav">
        <button onclick="switchTab('accounts')" id="tab-accounts-btn" class="tab-btn active">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
          <span>Caixas de E-mail</span>
        </button>
        <button onclick="switchTab('aliases')" id="tab-aliases-btn" class="tab-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>
          <span>Aliases & Redirecionamentos</span>
        </button>
      </div>

      <div style="display: flex; align-items: center; gap: 12px;">
        <div class="search-box">
          <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="search-input" oninput="filterData()" placeholder="Buscar por e-mail..." class="search-input">
        </div>

        <button onclick="openCreateModal()" class="btn btn-primary">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          <span>Nova Conta</span>
        </button>

        <button onclick="openCreateAliasModal()" class="btn btn-ghost">
          <span>+ Novo Alias</span>
        </button>
      </div>
    </div>

    <!-- Accounts View -->
    <div id="view-accounts" class="table-container">
      <div id="accounts-list">
        <div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 13px;">
          Carregando contas...
        </div>
      </div>
    </div>

    <!-- Aliases View -->
    <div id="view-aliases" class="table-container" style="display: none;">
      <div id="aliases-list">
        <div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 13px;">
          Carregando aliases...
        </div>
      </div>
    </div>

  </main>

  <!-- Create Account Modal -->
  <div id="create-modal" class="modal-backdrop">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">Criar Nova Caixa Postal</h3>
        <button onclick="closeModal('create-modal')" class="close-btn">&times;</button>
      </div>
      <form onsubmit="handleCreateAccount(event)">
        <div class="form-group">
          <label class="form-label">Endereço de E-mail</label>
          <div class="input-group">
            <input type="text" id="new-user" required placeholder="contato, rogger, financeiro">
            <span class="input-group-addon">@broscotech.com.br</span>
          </div>
        </div>

        <div class="form-group">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <label class="form-label" style="margin-bottom: 0;">Senha Segura</label>
            <button type="button" onclick="generatePassword('new-pass')" class="gen-pass-btn">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
              <span>Gerar Senha</span>
            </button>
          </div>
          <input type="text" id="new-pass" required placeholder="Defina a senha da conta" class="input-text">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px;">
          <button type="button" onclick="closeModal('create-modal')" class="btn btn-ghost">Cancelar</button>
          <button type="submit" class="btn btn-primary">Criar Caixa Postal</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Update Password Modal -->
  <div id="password-modal" class="modal-backdrop">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">Redefinir Senha</h3>
        <button onclick="closeModal('password-modal')" class="close-btn">&times;</button>
      </div>
      <form onsubmit="handleUpdatePassword(event)">
        <input type="hidden" id="edit-email">
        <div style="padding: 10px 14px; background: rgba(255,255,255,0.03); border: 1px solid var(--surface-border); border-radius: 8px; font-family: var(--font-mono); font-size: 13px; color: #ffffff; margin-bottom: 18px;" id="edit-email-label"></div>

        <div class="form-group">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <label class="form-label" style="margin-bottom: 0;">Nova Senha</label>
            <button type="button" onclick="generatePassword('edit-pass')" class="gen-pass-btn">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
              <span>Gerar Senha</span>
            </button>
          </div>
          <input type="text" id="edit-pass" required placeholder="Nova senha segura" class="input-text">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px;">
          <button type="button" onclick="closeModal('password-modal')" class="btn btn-ghost">Cancelar</button>
          <button type="submit" class="btn btn-primary">Atualizar Senha</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Create Alias Modal -->
  <div id="alias-modal" class="modal-backdrop">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">Criar Novo Alias / Encaminhamento</h3>
        <button onclick="closeModal('alias-modal')" class="close-btn">&times;</button>
      </div>
      <form onsubmit="handleCreateAlias(event)">
        <div class="form-group">
          <label class="form-label">Apelido (Endereço Público)</label>
          <input type="email" id="alias-source" required placeholder="ex: dev@broscotech.com.br" class="input-text">
        </div>

        <div class="form-group">
          <label class="form-label">Destinatário Real (Caixa que recebe)</label>
          <input type="email" id="alias-target" required placeholder="ex: rogger@broscotech.com.br" class="input-text">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px;">
          <button type="button" onclick="closeModal('alias-modal')" class="btn btn-ghost">Cancelar</button>
          <button type="submit" class="btn btn-primary">Criar Alias</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    let state = { accounts: [], aliases: [] };

    function toast(msg) {
      const box = document.getElementById('toast-box');
      const item = document.createElement('div');
      item.className = 'toast';
      item.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <span>${msg}</span>
      `;
      box.appendChild(item);
      setTimeout(() => item.remove(), 3500);
    }

    async function checkAuth() {
      const res = await fetch('/api/status');
      if (res.status === 401) {
        document.getElementById('login-modal').classList.add('show');
      } else {
        document.getElementById('login-modal').classList.remove('show');
        loadData();
      }
    }

    async function handleLogin(e) {
      e.preventDefault();
      const pass = document.getElementById('admin-pass').value;
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
      });
      if (res.ok) {
        document.getElementById('login-modal').classList.remove('show');
        document.getElementById('login-error').style.display = 'none';
        toast('Autenticado com sucesso!');
        loadData();
      } else {
        document.getElementById('login-error').style.display = 'block';
      }
    }

    async function logout() {
      await fetch('/api/logout', { method: 'POST' });
      location.reload();
    }

    async function loadData() {
      const res = await fetch('/api/accounts');
      if (!res.ok) return;
      state = await res.json();
      renderAccounts();
      renderAliases();
    }

    function filterData() {
      const query = document.getElementById('search-input').value.trim().toLowerCase();
      renderAccounts(query);
      renderAliases(query);
    }

    function renderAccounts(filter = '') {
      const container = document.getElementById('accounts-list');
      document.getElementById('stat-accounts').innerText = state.accounts.length;
      
      const filtered = state.accounts.filter(a => a.email.toLowerCase().includes(filter));
      if (!filtered.length) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 13px;">Nenhuma caixa postal encontrada.</div>';
        return;
      }

      container.innerHTML = filtered.map(acc => `
        <div class="mail-row">
          <div class="account-left">
            <div class="avatar">${acc.email[0].toUpperCase()}</div>
            <div class="account-details">
              <div class="email-name">
                <span>${acc.email}</span>
              </div>
              <div class="email-meta">Caixa Corporativa IMAP/SMTP</div>
            </div>
          </div>

          <div class="account-middle">
            <span class="stat-pill">Uso: ${acc.usage || '0 B'}</span>
            <span class="stat-pill">Cota: ${acc.quota || 'Ilimitada'}</span>
          </div>

          <div class="account-actions">
            <button onclick="copyToClipboard('${acc.email}', 'E-mail copiado!')" class="btn btn-action-small" title="Copiar E-mail">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1-2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
            <button onclick="openPasswordModal('${acc.email}')" class="btn btn-action-small" title="Alterar Senha">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3 3"/></svg>
              <span>Senha</span>
            </button>
            <button onclick="handleDeleteAccount('${acc.email}')" class="btn btn-danger-ghost" title="Excluir Caixa Postal">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </div>
        </div>
      `).join('');
    }

    function renderAliases(filter = '') {
      const container = document.getElementById('aliases-list');
      document.getElementById('stat-aliases').innerText = state.aliases.length;

      const filtered = state.aliases.filter(a => a.source.toLowerCase().includes(filter) || a.target.toLowerCase().includes(filter));
      if (!filtered.length) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 13px;">Nenhum alias configurado.</div>';
        return;
      }

      container.innerHTML = filtered.map(al => `
        <div class="mail-row">
          <div class="account-left">
            <div class="avatar" style="color: #a78bfa;">@</div>
            <div class="account-details">
              <div class="email-name" style="color: #c4b5fd;">
                <span>${al.source}</span>
              </div>
              <div class="email-meta">Apelido de Encaminhamento</div>
            </div>
          </div>

          <div class="account-middle">
            <div style="font-size: 13px; font-family: var(--font-mono); color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
              <span>${al.target}</span>
            </div>
          </div>

          <div class="account-actions">
            <button onclick="handleDeleteAlias('${al.source}')" class="btn btn-danger-ghost" title="Excluir Alias">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </td>
        </tr>
      `).join('');
    }

    function switchTab(tab) {
      if (tab === 'accounts') {
        document.getElementById('view-accounts').style.display = 'block';
        document.getElementById('view-aliases').style.display = 'none';
        document.getElementById('tab-accounts-btn').classList.add('active');
        document.getElementById('tab-aliases-btn').classList.remove('active');
      } else {
        document.getElementById('view-accounts').style.display = 'none';
        document.getElementById('view-aliases').style.display = 'block';
        document.getElementById('tab-accounts-btn').classList.remove('active');
        document.getElementById('tab-aliases-btn').classList.add('active');
      }
    }

    function openCreateModal() {
      generatePassword('new-pass');
      document.getElementById('create-modal').classList.add('show');
    }
    function openCreateAliasModal() {
      document.getElementById('alias-modal').classList.add('show');
    }
    function openPasswordModal(email) {
      document.getElementById('edit-email').value = email;
      document.getElementById('edit-email-label').innerText = email;
      generatePassword('edit-pass');
      document.getElementById('password-modal').classList.add('show');
    }
    function closeModal(id) {
      document.getElementById(id).classList.remove('show');
    }

    function generatePassword(targetId) {
      const chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
      let pass = '';
      for (let i = 0; i < 14; i++) {
        pass += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      document.getElementById(targetId).value = pass + '!@#';
    }

    function copyToClipboard(text, msg) {
      navigator.clipboard.writeText(text);
      toast(msg || 'Copiado para a área de transferência!');
    }

    async function handleCreateAccount(e) {
      e.preventDefault();
      const user = document.getElementById('new-user').value.trim().toLowerCase();
      const email = user.includes('@') ? user : `${user}@broscotech.com.br`;
      const pass = document.getElementById('new-pass').value;
      const res = await fetch('/api/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: pass })
      });
      if (res.ok) {
        closeModal('create-modal');
        document.getElementById('new-user').value = '';
        toast(`Conta ${email} criada com sucesso!`);
        loadData();
      } else {
        toast('Erro ao criar conta.');
      }
    }

    async function handleUpdatePassword(e) {
      e.preventDefault();
      const email = document.getElementById('edit-email').value;
      const pass = document.getElementById('edit-pass').value;
      const res = await fetch('/api/accounts/password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: pass })
      });
      if (res.ok) {
        closeModal('password-modal');
        toast(`Senha atualizada com sucesso!`);
        loadData();
      } else {
        toast('Erro ao atualizar senha.');
      }
    }

    async function handleDeleteAccount(email) {
      if (!confirm(`Tem certeza que deseja excluir permanentemente a caixa ${email}?`)) return;
      const res = await fetch('/api/accounts/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      if (res.ok) {
        toast(`Conta ${email} excluída.`);
        loadData();
      } else {
        toast('Erro ao excluir conta.');
      }
    }

    async function handleCreateAlias(e) {
      e.preventDefault();
      const source = document.getElementById('alias-source').value.trim().toLowerCase();
      const target = document.getElementById('alias-target').value.trim().toLowerCase();
      const res = await fetch('/api/aliases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, target })
      });
      if (res.ok) {
        closeModal('alias-modal');
        document.getElementById('alias-source').value = '';
        document.getElementById('alias-target').value = '';
        toast(`Alias ${source} criado!`);
        loadData();
      } else {
        toast('Erro ao criar alias.');
      }
    }

    async function handleDeleteAlias(source) {
      if (!confirm(`Excluir alias ${source}?`)) return;
      const res = await fetch('/api/aliases/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source })
      });
      if (res.ok) {
        toast(`Alias ${source} removido.`);
        loadData();
      } else {
        toast('Erro ao excluir alias.');
      }
    }

    checkAuth();
  </script>
</body>
</html>
"""

class MailAdminHandler(http.server.BaseHTTPRequestHandler):
    def is_authenticated(self):
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return False
        cookie = SimpleCookie(cookie_header)
        token = cookie.get("mail_admin_session")
        return bool(token and token.value in SESSIONS)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/manager", "/manager/"):
            body = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/status":
            if self.is_authenticated():
                self.send_json({"authenticated": True})
            else:
                self.send_json({"authenticated": False}, status=401)
            return

        if not self.is_authenticated():
            self.send_json({"error": "Unauthorized"}, status=401)
            return

        if path == "/api/accounts":
            accounts = []
            aliases = []
            try:
                proc = subprocess.run(["sudo", "docker", "exec", "mailserver", "setup", "email", "list"],
                                      capture_output=True, text=True, check=True)
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    m = re.match(r"\*\s+([^\s]+)\s*\(\s*([^\s]+)\s*/\s*([^\s]+)\s*\)\s*\[([^\]]+)\]", line)
                    if m:
                        email = m.group(1)
                        usage = f"{m.group(2)} ({m.group(4)})"
                        quota = "Ilimitada" if m.group(3) == "~" else m.group(3)
                        accounts.append({"email": email, "usage": usage, "quota": quota})
                    elif line.startswith("*"):
                        parts = line.lstrip("* ").split()
                        accounts.append({"email": parts[0], "usage": "0", "quota": "Ilimitada"})
            except Exception:
                pass

            alias_path = "/srv/essentials/volumes/mailserver/config/postfix-virtual.cf"
            if os.path.exists(alias_path):
                with open(alias_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = line.split()
                            if len(parts) >= 2:
                                aliases.append({"source": parts[0], "target": " ".join(parts[1:])})

            self.send_json({"accounts": accounts, "aliases": aliases})
            return

        self.send_json({"error": "Not Found"}, status=404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length)) if length > 0 else {}

        if path == "/api/login":
            if data.get("password") == ADMIN_PASS:
                token = secrets.token_hex(32)
                SESSIONS.add(token)
                self.send_response(200)
                self.send_header("Set-Cookie", f"mail_admin_session={token}; Path=/; HttpOnly; SameSite=Strict")
                self.send_json({"success": True})
            else:
                self.send_json({"error": "Invalid password"}, status=401)
            return

        if path == "/api/logout":
            cookie_header = self.headers.get("Cookie")
            if cookie_header:
                cookie = SimpleCookie(cookie_header)
                token = cookie.get("mail_admin_session")
                if token and token.value in SESSIONS:
                    SESSIONS.remove(token.value)
            self.send_response(200)
            self.send_header("Set-Cookie", "mail_admin_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_json({"success": True})
            return

        if not self.is_authenticated():
            self.send_json({"error": "Unauthorized"}, status=401)
            return

        if path == "/api/accounts":
            email = data.get("email")
            password = data.get("password")
            if not email or not password:
                self.send_json({"error": "Missing fields"}, status=400)
                return
            subprocess.run(["sudo", "docker", "exec", "mailserver", "setup", "email", "add", email, password], check=True)
            self.send_json({"success": True})
            return

        if path == "/api/accounts/password":
            email = data.get("email")
            password = data.get("password")
            if not email or not password:
                self.send_json({"error": "Missing fields"}, status=400)
                return
            subprocess.run(["sudo", "docker", "exec", "mailserver", "setup", "email", "update", email, password], check=True)
            self.send_json({"success": True})
            return

        if path == "/api/accounts/delete":
            email = data.get("email")
            if not email:
                self.send_json({"error": "Missing email"}, status=400)
                return
            subprocess.run(["sudo", "docker", "exec", "mailserver", "setup", "email", "del", email], check=True)
            self.send_json({"success": True})
            return

        if path == "/api/aliases":
            source = data.get("source")
            target = data.get("target")
            if not source or not target:
                self.send_json({"error": "Missing fields"}, status=400)
                return
            subprocess.run(["sudo", "docker", "exec", "mailserver", "setup", "alias", "add", source, target], check=True)
            self.send_json({"success": True})
            return

        if path == "/api/aliases/delete":
            source = data.get("source")
            if not source:
                self.send_json({"error": "Missing source"}, status=400)
                return
            subprocess.run(["sudo", "docker", "exec", "mailserver", "setup", "alias", "del", source], check=True)
            self.send_json({"success": True})
            return

        self.send_json({"error": "Not Found"}, status=404)

if __name__ == "__main__":
    print(f"Starting Mail Manager on port {PORT}...")
    server = http.server.HTTPServer(("127.0.0.1", PORT), MailAdminHandler)
    server.serve_forever()