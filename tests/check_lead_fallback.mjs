/** Offline test of existing WhatsApp/email fallback functions; no network or real lead created. */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const start = source.indexOf('function submitInquiry(event) {');
const end = source.indexOf('function openWechatModal()', start);
assert(start > 0 && end > start && end - start < 10000, 'Fallback function boundaries changed');

const opened = [];
const sandbox = {
  window: {
    open: (url, target) => opened.push({ url, target }),
    location: { href: '' }
  },
  console
};
vm.createContext(sandbox);
vm.runInContext(source.slice(start, end), sandbox);

const fields = {
  name: 'TEST_PERSON',
  contactType: 'wechat',
  contactValue: 'TEST_CONTACT_ID',
  city: 'Bangkok',
  destination: 'Shanghai',
  cargo: 'documents',
  weight: '1 kg',
  pickup: 'yes'
};
const form = {
  querySelector: (selector) => {
    const name = selector.match(/^\[name="([^"]+)"\]$/)?.[1];
    return name in fields ? {value: fields[name]} : null;
  }
};
sandbox.submitInquiry({preventDefault() {}, target: form});
assert.equal(opened.length, 1);
assert(opened[0].url.startsWith('https://wa.me/'));
const message = decodeURIComponent(new URL(opened[0].url).searchParams.get('text'));
assert(message.includes('TEST_CONTACT_ID'), 'Fallback WhatsApp message dropped contactValue');
assert(message.includes('wechat'), 'Fallback WhatsApp message dropped contactType');
assert(message.includes('Bangkok'));
sandbox.sendInquiryEmail(form, 'support@example.invalid');
const mail = sandbox.window.location.href;
assert(mail.startsWith('mailto:support@example.invalid?'));
const body = new URL(mail).searchParams.get('body');
assert(body.includes('TEST_CONTACT_ID'), 'Fallback email message dropped contactValue');
assert(body.includes('wechat'), 'Fallback email message dropped contactType');
console.log('PASS: fallback enquiry preserves actual contact type and value without network writes');
