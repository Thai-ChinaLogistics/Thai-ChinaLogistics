(function () {
  const cfg = window.ADS_LEAD_TRACKER_CONFIG || {};
  const API_BASE = String(cfg.apiBase || '').replace(/\/$/, '');
  const API_READY = API_BASE && !API_BASE.includes('替换成你的worker地址');
  const DEBUG = !!cfg.debug;
  const PHONE = String(cfg.whatsappNumber || '66839769828').replace(/[^0-9]/g, '');
  const FB_URL = cfg.facebookUrl || 'https://www.facebook.com/profile.php?id=61576232865352';
  const BUSINESS = cfg.businessLabel || '泰国寄中国物流';
  const WECHAT_ID = cfg.wechatId || 'THAICHINA-LOGISTICS';

  function log() { if (DEBUG) console.log.apply(console, ['[AdsLeadTracker]'].concat([].slice.call(arguments))); }
  function makeId(prefix) { return prefix + Date.now() + '-' + Math.random().toString(36).slice(2, 9); }
  function storageGet(key, prefix, store) {
    store = store || localStorage;
    let v = store.getItem(key);
    if (!v) { v = makeId(prefix); store.setItem(key, v); }
    return v;
  }
  function visitorId() { return storageGet('atl_visitor_id', 'V', localStorage); }
  function sessionId() { return storageGet('atl_session_id', 'S', sessionStorage); }
  function currentLang() {
    return (document.documentElement.getAttribute('data-lang') || navigator.language || 'zh').toLowerCase();
  }
  function t(key) {
    const lang = currentLang();
    const isEn = lang.startsWith('en');
    const isTh = lang.startsWith('th');
    const dict = {
      wechatLabel: isEn ? 'WeChat ID' : (isTh ? 'ไอดี WeChat' : '微信号'),
      wechatTitle: isEn ? 'Contact us on WeChat' : (isTh ? 'ติดต่อเราทาง WeChat' : '微信联系客服'),
      wechatTip: isEn ? 'Copy the WeChat ID, then open WeChat to add customer service.' : (isTh ? 'คัดลอกไอดี WeChat แล้วเปิด WeChat เพื่อเพิ่มฝ่ายบริการลูกค้า' : '复制微信号后，打开微信添加客服即可咨询。'),
      close: isEn ? 'Close' : (isTh ? 'ปิด' : '关闭'),
      copyWechat: isEn ? 'Copy WeChat ID' : (isTh ? 'คัดลอก WeChat ID' : '复制微信号'),
      copyOk: isEn ? 'WeChat ID copied. Please open WeChat and add our customer service.' : (isTh ? 'คัดลอกไอดี WeChat แล้ว กรุณาเปิด WeChat เพื่อเพิ่มฝ่ายบริการลูกค้า' : '微信号已复制，请打开微信添加客服咨询。'),
      wechatFallback: isEn ? 'Please add our WeChat customer service: ' : (isTh ? 'กรุณาเพิ่ม WeChat ฝ่ายบริการลูกค้า: ' : '请添加微信客服：'),
      trackFail: isEn ? 'The tracking service is temporarily unavailable. We will open the contact method for you first.' : (isTh ? 'ระบบบันทึกข้อมูลยังเชื่อมต่อไม่ได้ชั่วคราว จะเปิดช่องทางติดต่อให้ก่อน' : '追踪接口暂时无法连接，先为你打开联系方式。'),
      noApi: isEn ? 'Worker API is not configured. Contact method will open normally, but data will not be saved.' : (isTh ? 'ยังไม่ได้ตั้งค่า Worker API จะเปิดช่องทางติดต่อได้ตามปกติ แต่จะไม่บันทึกข้อมูล' : '还没有配置 Worker 地址，当前只做普通跳转，不会保存到后台。'),
      whatsappDefault: isEn ? 'Hello, I would like to ask about shipping from Thailand to China. Could you tell me the price and delivery time?' : (isTh ? 'สวัสดีค่ะ/ครับ ต้องการสอบถามเรื่องการส่งของจากประเทศไทยไปจีน ขอทราบราคาและระยะเวลาจัดส่งค่ะ/ครับ' : '你好，我想咨询泰国寄中国物流，请问价格和时效怎么计算？')
    };
    return dict[key] || '';
  }
  function params() {
    const p = new URLSearchParams(location.search);
    return {
      utm_source: p.get('utm_source') || '',
      utm_medium: p.get('utm_medium') || '',
      utm_campaign: p.get('utm_campaign') || '',
      utm_content: p.get('utm_content') || '',
      utm_term: p.get('utm_term') || '',
      utm_keyword: p.get('utm_keyword') || p.get('keyword') || '',
      gclid: p.get('gclid') || '',
      gbraid: p.get('gbraid') || '',
      wbraid: p.get('wbraid') || '',
      fbclid: p.get('fbclid') || '',
      ttclid: p.get('ttclid') || '',
      page_url: location.href,
      landing_page: location.href,
      referrer: document.referrer || '',
      title: document.title || '',
      device: /Android|iPhone|iPad|Mobile|Windows Phone/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
      language: document.documentElement.getAttribute('data-lang') || navigator.language || '',
      screen: (screen && screen.width ? screen.width + 'x' + screen.height : '')
    };
  }
  function basePayload(extra) {
    return Object.assign({
      visitor_id: visitorId(),
      session_id: sessionId(),
      business_label: BUSINESS,
      created_at: new Date().toISOString()
    }, params(), extra || {});
  }
  function post(path, data, beacon) {
    if (!API_READY) return Promise.resolve({ ok: false, reason: 'api_not_configured' });
    const body = JSON.stringify(data);
    const url = API_BASE + path;
    if (beacon && navigator.sendBeacon) {
      try {
        navigator.sendBeacon(url, new Blob([body], { type: 'application/json' }));
        return Promise.resolve({ ok: true, beacon: true });
      } catch (e) {}
    }
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      keepalive: !!beacon
    }).then(r => r.json().catch(() => ({ ok: r.ok }))).catch(err => ({ ok: false, error: err.message }));
  }
  function cleanCustomerMessage(message) {
    const msg = String(message || '').trim();
    if (!msg) return t('whatsappDefault');
    return msg
      .replace(/\n*\s*线索编号[:：].*$/gim, '')
      .replace(/\n*\s*Lead ID[:：].*$/gim, '')
      .replace(/\n*\s*รหัสลูกค้า[:：]?.*$/gim, '')
      .trim() || t('whatsappDefault');
  }
  function openWhatsapp(message) {
    const finalMessage = cleanCustomerMessage(message);
    window.open('https://wa.me/' + PHONE + '?text=' + encodeURIComponent(finalMessage), '_blank');
  }
  function fallbackOpen(channel, opts) {
    opts = opts || {};
    const leadId = makeId('LOCAL');
    if (channel === 'whatsapp') {
      openWhatsapp(opts.message || '');
      return { ok: false, fallback: true, lead_id: leadId };
    }
    if (channel === 'facebook') {
      window.open(FB_URL, '_blank');
      return { ok: false, fallback: true, lead_id: leadId };
    }
    if (channel === 'wechat') {
      showWechatModal({ lead_id: leadId, wechat_id: WECHAT_ID });
      return { ok: false, fallback: true, lead_id: leadId };
    }
  }
  function ensureFloatingContacts() {
    if (document.getElementById('atlContactRail')) return;
    const rail = document.createElement('div');
    rail.id = 'atlContactRail';
    rail.className = 'atl-contact-rail';
    rail.setAttribute('aria-label', 'Contact');
    rail.innerHTML =
      '<a class="atl-contact-btn atl-contact-whatsapp" data-lead-contact="whatsapp" data-label="WhatsApp" href="https://wa.me/' + PHONE + '" target="_blank" rel="noopener" aria-label="WhatsApp">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 3.5A11.8 11.8 0 0 0 12.1 0C5.6 0 .3 5.3.3 11.8c0 2.1.6 4.2 1.6 6L0 24l6.4-1.7a11.8 11.8 0 0 0 5.7 1.5h.1c6.5 0 11.8-5.3 11.8-11.8 0-3.2-1.2-6.2-3.5-8.5Zm-8.3 18.3h-.1a9.8 9.8 0 0 1-5-1.4l-.4-.2-3.8 1 1-3.7-.2-.4a9.7 9.7 0 0 1-1.5-5.2c0-5.4 4.4-9.8 9.9-9.8a9.8 9.8 0 0 1 9.8 9.8c0 5.4-4.4 9.8-9.7 9.9Zm5.4-7.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.2-.2.3-.8.9-1 1.1-.2.2-.4.2-.7.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.6.3-.5c.1-.2 0-.4 0-.5-.1-.1-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.2 3.3 5.3 4.6.7.3 1.3.5 1.8.6.8.2 1.5.2 2 .1.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.3.2-1.4 0-.1-.3-.2-.6-.3Z"/></svg>' +
      '</a>' +
      '<a class="atl-contact-btn atl-contact-facebook" data-lead-contact="facebook" data-label="Facebook" href="' + FB_URL + '" target="_blank" rel="noopener" aria-label="Facebook">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.7 24v-10h3.4l.5-3.9h-3.9V7.6c0-1.1.3-1.9 2-1.9h2.1V2.2c-.4 0-1.7-.2-3.1-.2-3.1 0-5.2 1.9-5.2 5.3v2.9H6v3.9h3.5v10h4.2Z"/></svg>' +
      '</a>' +
      '<button type="button" class="atl-contact-btn atl-contact-wechat" data-lead-contact="wechat" data-label="WeChat" aria-label="WeChat">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.1 3C4.1 3 0 6.3 0 10.4c0 2.3 1.3 4.3 3.3 5.7l-.8 2.5 2.9-1.5c1.1.4 2.3.7 3.7.7h.5a6.8 6.8 0 0 1-.2-1.7c0-3.8 3.6-6.9 8.1-6.9h.6C17.4 5.7 13.6 3 9.1 3Zm-3 4.2c.7 0 1.2.5 1.2 1.2S6.8 9.6 6.1 9.6 4.9 9.1 4.9 8.4 5.4 7.2 6.1 7.2Zm6.1 0c.7 0 1.2.5 1.2 1.2s-.5 1.2-1.2 1.2S11 9.1 11 8.4s.5-1.2 1.2-1.2Zm5.3 3.7c-3.6 0-6.5 2.3-6.5 5.2s2.9 5.2 6.5 5.2c1 0 1.9-.2 2.8-.5l2.1 1.1-.6-1.9c1.4-1 2.2-2.4 2.2-3.9 0-2.9-2.9-5.2-6.5-5.2Zm-2.2 3c-.5 0-.9-.4-.9-.9s.4-.9.9-.9.9.4.9.9-.4.9-.9.9Zm4.4 0c-.5 0-.9-.4-.9-.9s.4-.9.9-.9.9.4.9.9-.4.9-.9.9Z"/></svg>' +
      '</button>';
    document.body.appendChild(rail);
  }
  function ensureWechatModal() {
    let modal = document.getElementById('wechatModal');
    if (modal) return modal;
    modal = document.createElement('div');
    modal.id = 'wechatModal';
    modal.className = 'wechat-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML =
      '<div class="wechat-modal-card" role="document">' +
        '<button type="button" class="wechat-modal-close" aria-label="Close">×</button>' +
        '<div class="wechat-modal-icon" aria-hidden="true">微信</div>' +
        '<h3 class="wechat-modal-title"></h3>' +
        '<p class="wechat-tip"></p>' +
      '</div>';
    document.body.appendChild(modal);
    const close = () => {
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
    };
    modal.querySelector('.wechat-modal-close').addEventListener('click', close);
    modal.addEventListener('click', function (e) { if (e.target === modal) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && modal.classList.contains('active')) close(); });
    return modal;
  }
  function ensureWechatLeadBox() {
    ensureWechatModal();
    const card = document.querySelector('#wechatModal .wechat-modal-card');
    if (!card) return null;
    let box = document.getElementById('leadTrackerWechatBox');
    if (!box) {
      box = document.createElement('div');
      box.id = 'leadTrackerWechatBox';
      box.innerHTML = '<div style="margin:14px auto 0;padding:12px;border-radius:14px;background:#f4f8ff;border:1px solid rgba(77,141,255,.18);color:#1f2a3d;text-align:center;">' +
        '<div style="margin-top:2px;font-size:13px;color:#6a7890;"><span id="wechatIdLabel"></span>：<span id="wechatIdText"></span></div>' +
        '<button type="button" id="copyWechatTrackerBtn" style="margin-top:10px;border:0;border-radius:999px;padding:9px 14px;background:#2563eb;color:#fff;font-weight:800;cursor:pointer;"></button>' +
      '</div>';
      const tip = card.querySelector('.wechat-tip') || card.lastElementChild;
      if (tip && tip.parentNode === card) card.insertBefore(box, tip.nextSibling); else card.appendChild(box);
      const btn = box.querySelector('#copyWechatTrackerBtn');
      btn.addEventListener('click', copyWechat);
    }
    const label = document.getElementById('wechatIdLabel');
    const btn = document.getElementById('copyWechatTrackerBtn');
    const title = document.querySelector('#wechatModal .wechat-modal-title');
    const tip = document.querySelector('#wechatModal .wechat-tip');
    const close = document.querySelector('#wechatModal .wechat-modal-close');
    if (label) label.textContent = t('wechatLabel');
    if (btn) btn.textContent = t('copyWechat');
    if (title) title.textContent = t('wechatTitle');
    if (tip) tip.textContent = t('wechatTip');
    if (close) close.setAttribute('aria-label', t('close'));
    return box;
  }
  function showWechatModal(data) {
    ensureWechatLeadBox();
    const modal = document.getElementById('wechatModal');
    const wechatEl = document.getElementById('wechatIdText');
    if (wechatEl) wechatEl.textContent = data.wechat_id || WECHAT_ID || 'THAICHINA-LOGISTICS';
    if (modal) {
      modal.setAttribute('data-lead-id', data.lead_id || '');
      modal.classList.add('active');
      modal.setAttribute('aria-hidden', 'false');
      modal.style.display = '';
    } else {
      alert(t('wechatFallback') + (data.wechat_id || WECHAT_ID || 'THAICHINA-LOGISTICS'));
    }
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    const t = document.createElement('textarea');
    t.value = text; t.style.position = 'fixed'; t.style.opacity = '0';
    document.body.appendChild(t); t.select(); document.execCommand('copy'); document.body.removeChild(t);
    return Promise.resolve();
  }
  function copyWechat() {
    const modal = document.getElementById('wechatModal');
    const leadId = modal ? modal.getAttribute('data-lead-id') : '';
    const wechat = (document.getElementById('wechatIdText')?.textContent || WECHAT_ID || '').trim();
    copyText(wechat).then(() => {
      eventTrack('wechat_copy', 'wechat', leadId, { lead_id: leadId, wechat_id: wechat });
      alert(t('copyOk'));
    });
  }
  function eventTrack(type, channel, value, extra, beacon) {
    return post('/api/event', basePayload({
      event_type: type,
      channel: channel || '',
      event_value: value || '',
      extra: extra || {}
    }), !!beacon);
  }
  async function contact(channel, opts) {
    opts = opts || {};
    channel = String(channel || '').toLowerCase();
    if (!API_READY) {
      console.warn('[AdsLeadTracker] ' + t('noApi'));
      return fallbackOpen(channel, opts);
    }
    const cleanMessage = cleanCustomerMessage(opts.message || '');
    const res = await post('/api/contact', basePayload({
      channel,
      message: cleanMessage,
      source_button: opts.sourceButton || opts.source_button || '',
      lang: document.documentElement.getAttribute('data-lang') || navigator.language || ''
    }), false);
    log('contact result', res);
    if (!res || !res.ok) {
      alert(t('trackFail'));
      return fallbackOpen(channel, { message: cleanMessage });
    }
    if (channel === 'wechat') return showWechatModal(res);
    if (channel === 'whatsapp') {
      openWhatsapp(cleanMessage);
      return res;
    }
    if (channel === 'facebook') {
      window.open(res.redirect_url || FB_URL, '_blank');
      return res;
    }
    return fallbackOpen(channel, { message: cleanMessage });
  }
  function collectInquiryMessage(form) {
    const get = (name) => {
      const el = form.querySelector('[name="' + name + '"]');
      return el ? String(el.value || '').trim() : '';
    };
    const contactType = get('contactType');
    const contactValue = get('contactValue') || get('contact');
    return [
      '您好，咨询泰国发货到中国，请问是什么流程呢？',
      '',
      '【客户询价信息】',
      '姓名：' + (get('name') || '未填写'),
      '联系方式类型：' + (contactType || '未填写'),
      '联系方式：' + (contactValue || '未填写'),
      '泰国所在城市：' + (get('city') || '未填写'),
      '中国目的地：' + (get('destination') || '未填写'),
      '货物类型：' + (get('cargo') || '未填写'),
      '预估重量：' + (get('weight') || '未填写'),
      '包裹尺寸：' + (get('size') || '未填写'),
      '货物到仓途径：' + (get('pickup') || '未填写'),
      '备注：' + (get('note') || '未填写'),
      '',
      '请帮我报价并说明寄件流程，谢谢。'
    ].join('\n');
  }

  window.submitInquiry = function (event) {
    event.preventDefault();
    const form = event.target;
    const message = collectInquiryMessage(form);
    contact('whatsapp', { message, sourceButton: 'quote_form' });
  };

  document.addEventListener('click', function (e) {
    const el = e.target.closest('a,button');
    if (!el) return;
    if (el.closest('#wechatModal') && !el.classList.contains('social-btn')) return;
    const href = el.getAttribute('href') || '';
    const key = (el.getAttribute('data-lead-contact') || el.getAttribute('data-social-key') || '').toLowerCase();
    const isWhatsApp = key === 'whatsapp' || /wa\.me|api\.whatsapp\.com/i.test(href);
    const isFacebook = key === 'facebook' || (el.classList.contains('facebook') && /facebook\.com|m\.me/i.test(href));
    const isWechat = key === 'wechat' || el.classList.contains('wechat');
    if (!isWhatsApp && !isFacebook && !isWechat) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    if (isWhatsApp) return contact('whatsapp', { sourceButton: el.id || key || 'whatsapp_button', originalUrl: href });
    if (isFacebook) return contact('facebook', { sourceButton: el.id || key || 'facebook_button', originalUrl: href });
    if (isWechat) return contact('wechat', { sourceButton: el.id || key || 'wechat_button' });
  }, true);

  let maxScroll = 0;
  function sendVisit() { post('/api/visit', basePayload(), false).then(res => log('visit', res)); }
  function onScroll() {
    const total = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    const pct = Math.round((scrollY / total) * 100);
    if (pct >= 50 && maxScroll < 50) { maxScroll = 50; eventTrack('scroll_50', '', '50', {}, true); }
    if (pct >= 90 && maxScroll < 90) { maxScroll = 90; eventTrack('scroll_90', '', '90', {}, true); }
  }
  document.addEventListener('DOMContentLoaded', function () {
    ensureFloatingContacts();
    ensureWechatLeadBox();
    sendVisit();
    setTimeout(() => eventTrack('stay_10s', '', '10', {}, true), 10000);
    setTimeout(() => eventTrack('stay_30s', '', '30', {}, true), 30000);
  });
  if (document.readyState !== 'loading') { ensureFloatingContacts(); ensureWechatLeadBox(); sendVisit(); }
  window.addEventListener('scroll', function () {
    if (window.__atlScrollTimer) return;
    window.__atlScrollTimer = setTimeout(function () { window.__atlScrollTimer = null; onScroll(); }, 300);
  }, { passive: true });
  window.addEventListener('beforeunload', function () {
    eventTrack('page_leave', '', String(Math.round(performance.now() / 1000)), {
      stay_seconds: Math.round(performance.now() / 1000),
      max_scroll: maxScroll
    }, true);
  });
  window.AdsLeadTracker = { contact, event: eventTrack, copyWechat, apiReady: () => API_READY };
})();
