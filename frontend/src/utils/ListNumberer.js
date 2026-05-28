export const NUMBERING_FORMAT = {
  ARABIC: 'arabic',
  ROMAN: 'roman',
  ALPHABETIC: 'alphabetic',
  ALPHABETIC_UPPER: 'alphabetic-upper',
  ROMAN_LOWER: 'roman-lower',
  ALPHABETIC_PARENTHESES: 'alphabetic-parens',
  ROMAN_PARENTHESES: 'roman-parens',
  LEADING_ZERO: 'leading-zero',
};

const ARABIC_TO_ROMAN_MAP = [
  ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'],
  ['', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC'],
  ['', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM'],
  ['', 'M', 'MM', 'MMM', 'M\u0305V\u0305', 'V\u0305', 'V\u0305M\u0305', 'V\u0305M\u0305M\u0305', 'V\u0305M\u0305M\u0305M\u0305', 'X\u0305'],
];

const ARABIC_TO_ALPHA = 'abcdefghijklmnopqrstuvwxyz';

function toRoman(num) {
  if (num <= 0) return String(num);
  if (num >= 40000) {
    let result = '';
    let n = num;
    const mappings = [
      [900000, 'C\u0305M\u0305'], [500000, 'D\u0305'], [400000, 'C\u0305D\u0305'],
      [100000, 'C\u0305'], [90000, 'X\u0305C\u0305'], [50000, 'L\u0305'], [40000, 'X\u0305L\u0305'],
      [10000, 'X\u0305'], [9000, 'IX\u0305'], [5000, 'V\u0305'], [4000, 'IV\u0305'],
      [1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'],
      [100, 'C'], [90, 'XC'], [50, 'L'], [40, 'XL'],
      [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I'],
    ];
    for (const [value, symbol] of mappings) {
      while (n >= value) {
        result += symbol;
        n -= value;
      }
    }
    return result;
  }
  const thousands = Math.floor(num / 1000);
  const hundreds = Math.floor((num % 1000) / 100);
  const tens = Math.floor((num % 100) / 10);
  const ones = num % 10;
  let result = '';
  if (thousands > 0) result = 'M'.repeat(thousands);
  result += ARABIC_TO_ROMAN_MAP[2][hundreds] || '';
  result += ARABIC_TO_ROMAN_MAP[1][tens] || '';
  result += ARABIC_TO_ROMAN_MAP[0][ones] || '';
  return result || String(num);
}

function toAlphabetic(num, upper = false) {
  if (num <= 0) return String(num);
  let result = '';
  let n = num;
  while (n > 0) {
    n -= 1;
    result = (upper ? ARABIC_TO_ALPHA[n % 26].toUpperCase() : ARABIC_TO_ALPHA[n % 26]) + result;
    n = Math.floor(n / 26);
  }
  return result;
}

function toLeadingZero(num, width = 3) {
  return String(num).padStart(width, '0');
}

function formatNumber(num, fmt) {
  if (num <= 0) return String(num);
  switch (fmt) {
    case NUMBERING_FORMAT.ARABIC: return String(num);
    case NUMBERING_FORMAT.ROMAN: return toRoman(num);
    case NUMBERING_FORMAT.ROMAN_LOWER: return toRoman(num).toLowerCase();
    case NUMBERING_FORMAT.ALPHABETIC: return toAlphabetic(num, false);
    case NUMBERING_FORMAT.ALPHABETIC_UPPER: return toAlphabetic(num, true);
    case NUMBERING_FORMAT.ALPHABETIC_PARENTHESES: return `(${toAlphabetic(num, false)})`;
    case NUMBERING_FORMAT.ROMAN_PARENTHESES: return `(${toRoman(num).toLowerCase()})`;
    case NUMBERING_FORMAT.LEADING_ZERO: return toLeadingZero(num);
    default: return String(num);
  }
}

function isListItem(node) {
  return node && node.nodeType === Node.ELEMENT_NODE && node.tagName === 'LI';
}

function getDirectListParent(li) {
  let el = li.parentElement;
  while (el) {
    if (el.tagName === 'OL' || el.tagName === 'UL') {
      if (el.closest('[data-list-numberer-ignore]')) return null;
      return el;
    }
    el = el.parentElement;
  }
  return null;
}

function getItemFlatIndex(li) {
  const list = getDirectListParent(li);
  if (!list) return 1;
  return Array.from(list.querySelectorAll(':scope > li')).indexOf(li) + 1;
}

function buildNumberPath(li, fmt) {
  const parts = [];
  let current = li;
  while (current && current.tagName === 'LI') {
    const list = getDirectListParent(current);
    if (!list) break;
    const items = Array.from(list.querySelectorAll(':scope > li'));
    const idx = items.indexOf(current) + 1;
    const listFmt = list.dataset.numberingFormat || fmt;
    parts.unshift(formatNumber(idx, listFmt));
    const parentLi = list.parentElement;
    if (!parentLi || parentLi.tagName !== 'LI') break;
    current = parentLi;
  }
  return parts.join('.');
}

function getListDepth(li) {
  let depth = 0;
  let el = li.parentElement;
  while (el && el.tagName !== 'BODY') {
    if (el.tagName === 'OL' || el.tagName === 'UL') {
      depth++;
    }
    el = el.parentElement;
  }
  return depth;
}

function buildHierarchyNumber(li, fmt) {
  return buildNumberPath(li, fmt);
}

function applyNumberToElement(li, numberStr) {
  let counter = li.querySelector('.list-item-counter');
  if (!counter) {
    counter = document.createElement('span');
    counter.className = 'list-item-counter';
    counter.setAttribute('aria-hidden', 'true');
    counter.style.cssText = [
      'display:inline-block',
      'min-width:1.5em',
      'text-align:right',
      'margin-right:0.5em',
      'color:var(--list-number-color,#4a9eff)',
      'font-family:var(--list-number-font,monospace)',
      'font-weight:600',
    ].join(';');
    li.insertBefore(counter, li.firstChild);
  }
  counter.textContent = numberStr;
  li.setAttribute('data-list-number', numberStr);
  li.setAttribute('aria-posinset', String(getItemFlatIndex(li)));
  li.setAttribute('aria-level', String(getListDepth(li)));
}

function renderList(list, options = {}) {
  const {
    format = NUMBERING_FORMAT.ARABIC,
    numberingType = 'injected',
    separator = '.',
    showHierarchy = true,
  } = options;

  if (list.closest('[data-list-numberer-ignore]')) return;

  const numberingFormat = list.dataset.numberingFormat || format;
  const directItems = Array.from(list.querySelectorAll(':scope > li'));

  function processItem(li, siblingIndex) {
    if (!isListItem(li)) return;

    let numberStr;
    if (showHierarchy) {
      numberStr = buildHierarchyNumber(li, numberingFormat);
    } else {
      numberStr = formatNumber(siblingIndex, numberingFormat);
    }

    if (numberingType === 'injected') {
      applyNumberToElement(li, numberStr);
    } else if (numberingType === 'counter') {
      li.style.listStyleType = 'none';
      li.style.counterIncrement = `list-num-${siblingIndex}`;
    }

    const nestedLists = Array.from(li.querySelectorAll(':scope > ol, :scope > ul'));
    nestedLists.forEach(nestedList => {
      const nestedItems = Array.from(nestedList.querySelectorAll(':scope > li'));
      nestedItems.forEach((nestedLi, ni) => {
        processItem(nestedLi, showHierarchy ? ni + 1 : null);
      });
    });
  }

  if (!showHierarchy) {
    let globalCounter = 1;
    function flattenProcess(li) {
      if (!isListItem(li)) return;
      applyNumberToElement(li, formatNumber(globalCounter, numberingFormat));
      globalCounter++;
      const nestedLists = Array.from(li.querySelectorAll(':scope > ol, :scope > ul'));
      nestedLists.forEach(nestedList => {
        Array.from(nestedList.querySelectorAll(':scope > li')).forEach(nestedLi => flattenProcess(nestedLi));
      });
    }
    directItems.forEach(li => flattenProcess(li));
  } else {
    directItems.forEach((li, i) => processItem(li, i + 1));
  }
}

class ListNumberer {
  constructor(selector, options = {}) {
    this.options = {
      format: NUMBERING_FORMAT.ARABIC,
      numberingType: 'injected',
      separator: '.',
      showHierarchy: true,
      hierarchySeparator: '.',
      autoUpdate: true,
      mutationTimeout: 100,
      ...options,
    };
    if (typeof selector === 'string') {
      this.lists = Array.from(document.querySelectorAll(selector));
    } else if (Array.isArray(selector)) {
      this.lists = selector.map(s => typeof s === 'string' ? document.querySelector(s) : s).filter(Boolean);
    } else {
      this.lists = [selector];
    }
    this.observer = null;
    this._debounceTimer = null;
    this._enabled = true;
    this._createObserver();
    this.refresh();
    if (!this.options.autoUpdate) {
      this._enabled = false;
    }
  }

  _createObserver() {
    if (typeof MutationObserver === 'undefined') return;
    const configs = { childList: true, subtree: true, characterData: true };
    const processMutations = () => {
      clearTimeout(this._debounceTimer);
      this._debounceTimer = setTimeout(() => {
        if (this._enabled) this.refresh();
      }, this.options.mutationTimeout);
    };
    this.observer = new MutationObserver(processMutations);
    this.lists.forEach(list => this.observer.observe(list, configs));
  }

  refresh() {
    this.lists.forEach(list => renderList(list, this.options));
  }

  setFormat(fmt) {
    this.options.format = fmt;
    this.refresh();
  }

  setNumberingType(type) {
    this.options.numberingType = type;
    this.refresh();
  }

  setHierarchyEnabled(enabled) {
    this.options.showHierarchy = enabled;
    this.refresh();
  }

  setEnabled(enabled) {
    this._enabled = enabled;
    if (enabled) this.refresh();
  }

  addItem(listIndex, li) {
    if (listIndex < 0 || listIndex >= this.lists.length) return;
    const list = this.lists[listIndex];
    list.appendChild(li);
    this.refresh();
  }

  removeItem(li) {
    if (li.parentElement) li.parentElement.removeChild(li);
    this.refresh();
  }

  moveItem(fromLi, toListIndex, toLi) {
    if (toListIndex < 0 || toListIndex >= this.lists.length) return;
    const toList = this.lists[toListIndex];
    if (toLi && toLi.parentElement === toList) {
      toList.insertBefore(fromLi, toLi);
    } else {
      toList.appendChild(fromLi);
    }
    this.refresh();
  }

  destroy() {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    this.lists.forEach(list => {
      Array.from(list.querySelectorAll('.list-item-counter')).forEach(el => el.remove());
    });
    this.lists = [];
  }
}

function createListNumberer(selector, options) {
  return new ListNumberer(selector, options);
}

function getAccessibleLabel(li, number) {
  const depth = getListDepth(li);
  li.setAttribute('aria-level', String(depth));
  return `${number}${depth > 1 ? `, nivelul ${depth}` : ''}`;
}

function patchAccessibleNumbering() {
  document.addEventListener('DOMNodeInserted', e => {
    if (isListItem(e.target)) {
      const counter = e.target.querySelector('.list-item-counter');
      if (counter) {
        getAccessibleLabel(e.target, counter.textContent);
      }
    }
  }, true);
}

export {
  ListNumberer,
  createListNumberer,
  renderList,
  formatNumber,
  getListDepth,
  buildHierarchyNumber,
  patchAccessibleNumbering,
  getAccessibleLabel,
};

export default ListNumberer;
