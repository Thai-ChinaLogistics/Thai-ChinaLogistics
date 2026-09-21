(function () {
  'use strict';
  if (window.__prdEnhancementsLoaded) return;
  window.__prdEnhancementsLoaded = true;

  var path = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  var isHome = path === '' || path === 'index.html';
  var copy = {
    'index.html': {
      title: '直接答案：泰中双向物流如何选择',
      answer: '泰国寄中国或中国寄泰国，应先提供起运城市、目的地、货物类型、重量、尺寸和时效要求，再比较空运、陆运、海运、取件、清关与末端派送。价格和可寄范围以实际货物审核为准。',
      cards: [['空运', '适合急件、小包、文件、样品和时间要求较高的货物。'], ['陆运', '适合预算敏感、批量或较大货物，时效按当期路线确认。'], ['海运/门到门', '适合大体积或非紧急货物，港口、清关和派送需逐票确认.']],
      cta: '提交城市、货物、重量和尺寸，获取针对性方案。'
    },
    'china-to-thailand.html': {
      title: '直接答案：中国寄泰国如何开始',
      answer: '淘宝、1688、供应商或中国仓库订单，可先确认代收、集货、合箱和包装，再按货物与泰国完整地址比较空运、陆运、海运或门到门路线。',
      cards: [['仓库代收', '适合多个店铺订单，先核对入仓、数量、照片和外箱。'], ['方式对比', '急件先比较空运；批量、大件再比较陆运或其他可用线路。'], ['商业货物', '发票、装箱单、HS Code、清关责任和末端派送逐票审核。']],
      cta: '提交中国起运地、泰国地址和货物资料。'
    },
    'thailand-to-china-express.html': { title: '直接答案：泰国快递到中国怎么选', answer: '小包、文件和个人物品先按品名、数量、重量、尺寸、取件城市和中国目的地审核，再比较空运、陆运或门到门方案。', cards: [['小包文件', '先提供品名、数量和收发件信息。'], ['空运', '适合急件、文件和小件。'], ['门到门', '取件、清关和中国末端派送统一评估。']], cta: '提交快递资料获取报价。' },
    'thailand-to-china-price.html': { title: '直接答案：泰国寄中国运费怎么算', answer: '通常同时比较实际重量和体积重量，取较大值作为计费基础，再叠加货物、起运城市、目的地、包装、取件、清关和派送因素。', cards: [['重量', '提供实际重量、外箱长宽高和件数。'], ['路线', '空运、陆运及其他可用线路按当期确认。'], ['服务', '特殊品类、包装、取件和派送单独审核。']], cta: '提交重量、尺寸和路线资料。' },
    'thailand-to-china-pickup.html': { title: '直接答案：泰国上门取件怎么衔接寄中国', answer: '酒店、公寓、商场、门店、仓库或供应商地址都应先确认交接条件，再按货物审核结果确认包装、空运、陆运和中国派送。', cards: [['酒店遗失物', '确认前台交接、授权、时间和物品信息。'], ['门店仓库', '提供完整地址、联系人、箱数和可取时间。'], ['运输衔接', '取件费与国际运输费分开核算。']], cta: '提交完整取件地址和货物照片。' }
  };
  var cityNames = {
    'bangkok-to-china.html': '曼谷', 'phuket-to-china.html': '普吉岛', 'chiang-mai-to-china.html': '清迈', 'pattaya-to-china.html': '芭提雅',
    'koh-samui-to-china.html': '苏梅岛', 'hat-yai-to-china.html': '合艾', 'chiang-rai-to-china.html': '清莱'
  };
  if (!copy[path] && cityNames[path]) {
    copy[path] = { title: '直接答案：' + cityNames[path] + '寄中国怎么选', answer: cityNames[path] + '寄中国可咨询上门取件、空运、陆运和中国派送。请先提供完整取件地址、货物类型、重量、尺寸和目的地，价格、可寄范围与时效按实际审核确认。', cards: [['本地取件', cityNames[path] + '酒店、公寓、商场、仓库或供应商地址按交接条件确认。'], ['货物审核', '食品、液体、粉末、电子产品、电池和品牌商品需提前核对。'], ['路线报价', '根据重量、体积、货物和中国目的地比较运输方式。']], cta: '提交' + cityNames[path] + '取件和货物资料。' };
  }
  if (!copy[path]) {
    copy[path] = { title: '直接答案：发货前需要确认什么', answer: '请先提供货物照片或品名、数量、重量、尺寸、起运城市和目的地，再确认可寄范围、运输方式、包装、清关、派送和报价。', cards: [['货物', '普通、特殊和商业货物按实际资料审核。'], ['运输', '空运、陆运、海运和门到门按时效与预算比较。'], ['交付', '取件、包装、清关和末端派送逐项确认。']], cta: '提交完整资料获取方案。' };
  }
  function esc(value) { return String(value).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }
  function addBlock() {
    if (isHome || document.querySelector('[data-prd-enhancement]')) return;
    var main = document.querySelector('main');
    if (!main) return;
    var d = copy[path];
    var block = document.createElement('section');
    block.className = 'prd-answer-block container';
    block.setAttribute('data-prd-enhancement', 'true');
    block.innerHTML = '<h2>' + esc(d.title) + '</h2><p>' + esc(d.answer) + '</p><div class="prd-grid">' + d.cards.map(function (card) { return '<article><h3>' + esc(card[0]) + '</h3><p>' + esc(card[1]) + '</p></article>'; }).join('') + '</div><div class="prd-steps"><div><strong>1. 提供资料</strong><p>照片、品名、数量、重量和尺寸。</p></div><div><strong>2. 提供路线</strong><p>起运城市和完整目的地地址。</p></div><div><strong>3. 审核报价</strong><p>确认可寄、包装、运输和费用。</p></div><div><strong>4. 安排发货</strong><p>确认后衔接取件、清关和派送。</p></div></div><div class="prd-cta"><span>' + esc(d.cta) + '</span><a class="btn" href="index.html#contact">立即询价</a></div>';
    main.appendChild(block);
  }
  function init() { addBlock(); document.documentElement.setAttribute('data-prd-ready', 'true'); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
}());
