import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  ListNumberer,
  createListNumberer,
  formatNumber,
  getListDepth,
  buildHierarchyNumber,
  renderList,
  NUMBERING_FORMAT,
  getAccessibleLabel,
} from './ListNumberer.js';

function createListHTML(items, nested = [], formatAttr = '') {
  const nestedHTML = nested.length > 0
    ? nested.map(n => `<li>${n}</li>`).join('')
    : '';
  const olAttrs = formatAttr ? ` data-numbering-format="${formatAttr}"` : '';
  return `<ol${olAttrs}>${items.map((t, i) => {
    const nestedPart = nested.length > 0 && i === 0 ? `<ol>${nestedHTML}</ol>` : '';
    return `<li>${t}${nestedPart}</li>`;
  }).join('')}</ol>`;
}

function makeContainer(html) {
  const div = document.createElement('div');
  div.innerHTML = html;
  document.body.appendChild(div);
  return div;
}

function getContainer() {
  return document.querySelector('div');
}

describe('formatNumber', () => {
  it('format arabic returns string number', () => {
    expect(formatNumber(1, NUMBERING_FORMAT.ARABIC)).toBe('1');
    expect(formatNumber(99, NUMBERING_FORMAT.ARABIC)).toBe('99');
    expect(formatNumber(0, NUMBERING_FORMAT.ARABIC)).toBe('0');
    expect(formatNumber(-1, NUMBERING_FORMAT.ARABIC)).toBe('-1');
  });

  it('format roman converts correctly', () => {
    expect(formatNumber(1, NUMBERING_FORMAT.ROMAN)).toBe('I');
    expect(formatNumber(4, NUMBERING_FORMAT.ROMAN)).toBe('IV');
    expect(formatNumber(9, NUMBERING_FORMAT.ROMAN)).toBe('IX');
    expect(formatNumber(10, NUMBERING_FORMAT.ROMAN)).toBe('X');
    expect(formatNumber(50, NUMBERING_FORMAT.ROMAN)).toBe('L');
    expect(formatNumber(100, NUMBERING_FORMAT.ROMAN)).toBe('C');
    expect(formatNumber(3999, NUMBERING_FORMAT.ROMAN)).toBe('MMMCMXCIX');
    expect(formatNumber(0, NUMBERING_FORMAT.ROMAN)).toBe('0');
  });

  it('format roman-lower converts to lowercase', () => {
    expect(formatNumber(4, NUMBERING_FORMAT.ROMAN_LOWER)).toBe('iv');
    expect(formatNumber(10, NUMBERING_FORMAT.ROMAN_LOWER)).toBe('x');
  });

  it('format alphabetic converts correctly', () => {
    expect(formatNumber(1, NUMBERING_FORMAT.ALPHABETIC)).toBe('a');
    expect(formatNumber(26, NUMBERING_FORMAT.ALPHABETIC)).toBe('z');
    expect(formatNumber(27, NUMBERING_FORMAT.ALPHABETIC)).toBe('aa');
    expect(formatNumber(28, NUMBERING_FORMAT.ALPHABETIC)).toBe('ab');
    expect(formatNumber(52, NUMBERING_FORMAT.ALPHABETIC)).toBe('az');
    expect(formatNumber(53, NUMBERING_FORMAT.ALPHABETIC)).toBe('ba');
  });

  it('format alphabetic-upper converts to uppercase', () => {
    expect(formatNumber(1, NUMBERING_FORMAT.ALPHABETIC_UPPER)).toBe('A');
    expect(formatNumber(27, NUMBERING_FORMAT.ALPHABETIC_UPPER)).toBe('AA');
  });

  it('format alphabetic-parens wraps in parentheses', () => {
    expect(formatNumber(1, NUMBERING_FORMAT.ALPHABETIC_PARENTHESES)).toBe('(a)');
    expect(formatNumber(3, NUMBERING_FORMAT.ALPHABETIC_PARENTHESES)).toBe('(c)');
  });

  it('format roman-parens wraps in parentheses', () => {
    expect(formatNumber(1, NUMBERING_FORMAT.ROMAN_PARENTHESES)).toBe('(i)');
    expect(formatNumber(4, NUMBERING_FORMAT.ROMAN_PARENTHESES)).toBe('(iv)');
  });

  it('format leading-zero pads with zeros', () => {
    expect(formatNumber(1, NUMBERING_FORMAT.LEADING_ZERO)).toBe('001');
    expect(formatNumber(42, NUMBERING_FORMAT.LEADING_ZERO)).toBe('042');
    expect(formatNumber(999, NUMBERING_FORMAT.LEADING_ZERO)).toBe('999');
  });

  it('unknown format falls back to arabic', () => {
    expect(formatNumber(5, 'unknown')).toBe('5');
  });
});

describe('getListDepth', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('top-level li has depth 1', () => {
    const html = createListHTML(['Item 1', 'Item 2']);
    const container = makeContainer(html);
    const li = container.querySelector('li');
    expect(getListDepth(li)).toBe(1);
  });

  it('nested li has depth 2', () => {
    const html = createListHTML(['Item 1'], ['Nested 1', 'Nested 2']);
    const container = makeContainer(html);
    const nestedLi = container.querySelectorAll('li')[1];
    expect(getListDepth(nestedLi)).toBe(2);
  });

  it('deeply nested li has correct depth', () => {
    document.body.innerHTML = `
      <ol>
        <li>A
          <ol>
            <li>B
              <ol>
                <li>C</li>
              </ol>
            </li>
          </ol>
        </li>
      </ol>
    `;
    const liC = document.body.querySelectorAll('li')[2];
    expect(getListDepth(liC)).toBe(3);
  });
});

describe('buildHierarchyNumber', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('flat list returns sequential numbers', () => {
    const html = createListHTML(['A', 'B', 'C']);
    const container = makeContainer(html);
    const items = container.querySelectorAll('li');
    expect(buildHierarchyNumber(items[0], NUMBERING_FORMAT.ARABIC)).toBe('1');
    expect(buildHierarchyNumber(items[1], NUMBERING_FORMAT.ARABIC)).toBe('2');
    expect(buildHierarchyNumber(items[2], NUMBERING_FORMAT.ARABIC)).toBe('3');
  });

  it('nested list returns hierarchical path', () => {
    const html = createListHTML(['A'], ['Nested']);
    const container = makeContainer(html);
    const items = container.querySelectorAll('li');
    expect(buildHierarchyNumber(items[0], NUMBERING_FORMAT.ARABIC)).toBe('1');
    expect(buildHierarchyNumber(items[1], NUMBERING_FORMAT.ARABIC)).toBe('1.1');
  });

  it('two-level deep nesting returns correct paths', () => {
    document.body.innerHTML = `
      <ol>
        <li>Level 1
          <ol>
            <li>Level 2 Item
              <ol>
                <li>Level 3 Item</li>
              </ol>
            </li>
          </ol>
        </li>
        <li>Level 1 Item 2</li>
      </ol>
    `;
    const items = document.body.querySelectorAll('li');
    expect(buildHierarchyNumber(items[0], NUMBERING_FORMAT.ARABIC)).toBe('1');
    expect(buildHierarchyNumber(items[1], NUMBERING_FORMAT.ARABIC)).toBe('1.1');
    expect(buildHierarchyNumber(items[2], NUMBERING_FORMAT.ARABIC)).toBe('1.1.1');
    expect(buildHierarchyNumber(items[3], NUMBERING_FORMAT.ARABIC)).toBe('2');
  });

  it('respects data-numbering-format on list element', () => {
    const html = createListHTML(['A', 'B'], [], 'roman');
    const container = makeContainer(html);
    const items = container.querySelectorAll('li');
    expect(buildHierarchyNumber(items[0], NUMBERING_FORMAT.ARABIC)).toBe('I');
    expect(buildHierarchyNumber(items[1], NUMBERING_FORMAT.ARABIC)).toBe('II');
  });
});

describe('renderList', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('injects numbers into li elements', () => {
    const html = createListHTML(['Alpha', 'Beta', 'Gamma']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected' });
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters.length).toBe(3);
    expect(counters[0].textContent).toBe('1');
    expect(counters[1].textContent).toBe('2');
    expect(counters[2].textContent).toBe('3');
  });

  it('updates data-list-number attribute', () => {
    const html = createListHTML(['One', 'Two']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected' });
    const items = container.querySelectorAll('li');
    expect(items[0].dataset.listNumber).toBe('1');
    expect(items[1].dataset.listNumber).toBe('2');
  });

  it('supports roman format', () => {
    const html = createListHTML(['I', 'II', 'III', 'IV']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ROMAN, numberingType: 'injected' });
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[0].textContent).toBe('I');
    expect(counters[3].textContent).toBe('IV');
  });

  it('supports alphabetic format', () => {
    const html = createListHTML(['a', 'b', 'c', 'd']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ALPHABETIC, numberingType: 'injected' });
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[0].textContent).toBe('a');
    expect(counters[3].textContent).toBe('d');
  });

  it('supports alphabetic-upper format', () => {
    const html = createListHTML(['A', 'B']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ALPHABETIC_UPPER, numberingType: 'injected' });
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[0].textContent).toBe('A');
    expect(counters[1].textContent).toBe('B');
  });

  it('renders nested items with hierarchy', () => {
    const html = createListHTML(['Parent'], ['Child']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected', showHierarchy: true });
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters.length).toBe(2);
    expect(counters[0].textContent).toBe('1');
    expect(counters[1].textContent).toBe('1.1');
  });

  it('showHierarchy=false renders flat numbers', () => {
    const html = createListHTML(['P'], ['C']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected', showHierarchy: false });
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[1].textContent).toBe('2');
  });

  it('ignores lists with data-list-numberer-ignore attribute', () => {
    document.body.innerHTML = `
      <ol data-list-numberer-ignore>
        <li>Should not number</li>
      </ol>
    `;
    const list = document.body.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected' });
    const counter = list.querySelector('.list-item-counter');
    expect(counter).toBeNull();
  });
});

describe('ListNumberer class', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('instantiates with selector string', () => {
    const html = createListHTML(['A', 'B']);
    makeContainer(html);
    const numberer = new ListNumberer('ol', { autoUpdate: false });
    expect(numberer.lists.length).toBe(1);
    expect(numberer.observer).not.toBeNull();
    numberer.destroy();
  });

  it('instantiates with element reference', () => {
    const html = createListHTML(['A', 'B']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: false });
    expect(numberer.lists.length).toBe(1);
    numberer.destroy();
  });

  it('refresh updates all counters', () => {
    const html = createListHTML(['X', 'Y', 'Z']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: false });
    numberer.refresh();
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[0].textContent).toBe('1');
    expect(counters[1].textContent).toBe('2');
    expect(counters[2].textContent).toBe('3');
    numberer.destroy();
  });

  it('setFormat changes numbering format', () => {
    const html = createListHTML(['A', 'B']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: false, format: NUMBERING_FORMAT.ARABIC });
    numberer.setFormat(NUMBERING_FORMAT.ROMAN);
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[0].textContent).toBe('I');
    expect(counters[1].textContent).toBe('II');
    numberer.destroy();
  });

  it('setHierarchyEnabled toggles hierarchy', () => {
    const html = createListHTML(['P'], ['C']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: false });
    numberer.setHierarchyEnabled(false);
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[1].textContent).toBe('2');
    numberer.destroy();
  });

  it('addItem appends li and refreshes', () => {
    const html = createListHTML(['A', 'B']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: false });
    const newLi = document.createElement('li');
    newLi.textContent = 'C';
    numberer.addItem(0, newLi);
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters.length).toBe(3);
    expect(counters[2].textContent).toBe('3');
    numberer.destroy();
  });

  it('removeItem removes li', () => {
    const html = createListHTML(['A', 'B', 'C']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: false });
    const li = container.querySelectorAll('li')[1];
    numberer.removeItem(li);
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters.length).toBe(2);
    expect(counters[0].textContent).toBe('1');
    expect(counters[1].textContent).toBe('2');
    numberer.destroy();
  });

  it('moveItem moves li and refreshes', () => {
    const html = createListHTML(['A', 'B', 'C']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: false });
    const liA = container.querySelectorAll('li')[0];
    const liC = container.querySelectorAll('li')[2];
    numberer.moveItem(liA, 0, liC);
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters[0].textContent).toBe('1');
    expect(counters[1].textContent).toBe('2');
    numberer.destroy();
  });

  it('setEnabled false stops auto-updates', () => {
    const html = createListHTML(['A']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: true });
    numberer.setEnabled(false);
    const li = document.createElement('li');
    li.textContent = 'B';
    list.appendChild(li);
    const counters = container.querySelectorAll('.list-item-counter');
    expect(counters.length).toBe(1);
    numberer.destroy();
  });

  it('destroy disconnects observer and removes counters', () => {
    const html = createListHTML(['A', 'B']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: true });
    numberer.destroy();
    expect(numberer.observer).toBeNull();
    expect(container.querySelectorAll('.list-item-counter').length).toBe(0);
  });

  it('multiple lists get numbered independently', () => {
    document.body.innerHTML = `
      <ol id="list1"><li>A</li><li>B</li></ol>
      <ol id="list2"><li>X</li><li>Y</li></ol>
    `;
    const numberer = new ListNumberer(['#list1', '#list2'], { autoUpdate: false });
    numberer.refresh();
    const counters = document.body.querySelectorAll('.list-item-counter');
    expect(counters.length).toBe(4);
    expect(counters[0].textContent).toBe('1');
    expect(counters[2].textContent).toBe('1');
    numberer.destroy();
  });
});

describe('MutationObserver — auto-update', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    vi.useFakeTimers();
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.useRealTimers();
  });

  it('adding li triggers re-render after debounce', () => {
    const html = createListHTML(['A', 'B']);
    makeContainer(html);
    const list = document.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: true, mutationTimeout: 100 });
    expect(numberer.observer).not.toBeNull();
    const newLi = document.createElement('li');
    newLi.textContent = 'C';
    list.appendChild(newLi);
    expect(numberer.observer).not.toBeNull();
    vi.advanceTimersByTime(200);
    const counters = document.querySelectorAll('.list-item-counter');
    expect(counters.length).toBeGreaterThanOrEqual(2);
    numberer.destroy();
  });

  it('removing li triggers re-render after debounce', () => {
    const html = createListHTML(['A', 'B', 'C']);
    makeContainer(html);
    const list = document.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: true, mutationTimeout: 100 });
    expect(numberer.observer).not.toBeNull();
    const liB = document.querySelectorAll('li')[1];
    liB.remove();
    vi.advanceTimersByTime(200);
    const remaining = document.querySelectorAll('.list-item-counter');
    expect(remaining.length).toBeGreaterThanOrEqual(2);
    numberer.destroy();
  });

  it('character data change triggers re-render', () => {
    const html = createListHTML(['Alpha']);
    makeContainer(html);
    const list = document.querySelector('ol');
    const numberer = new ListNumberer(list, { autoUpdate: true, mutationTimeout: 100 });
    expect(document.querySelectorAll('.list-item-counter').length).toBe(1);
    const li = document.querySelector('li');
    li.firstChild.textContent = 'Beta';
    vi.advanceTimersByTime(150);
    expect(document.querySelectorAll('.list-item-counter').length).toBe(1);
    numberer.destroy();
  });
});

describe('accessibility', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('li receives aria-level attribute', () => {
    const html = createListHTML(['Level 1', 'Level 2']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected' });
    const items = container.querySelectorAll('li');
    expect(items[0].getAttribute('aria-level')).toBeTruthy();
    expect(items[1].getAttribute('aria-level')).toBeTruthy();
  });

  it('li receives aria-posinset attribute', () => {
    const html = createListHTML(['A', 'B', 'C']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected' });
    const items = container.querySelectorAll('li');
    expect(items[0].getAttribute('aria-posinset')).toBe('1');
    expect(items[1].getAttribute('aria-posinset')).toBe('2');
    expect(items[2].getAttribute('aria-posinset')).toBe('3');
  });

  it('counter has aria-hidden true', () => {
    const html = createListHTML(['Test']);
    const container = makeContainer(html);
    const list = container.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected' });
    const counter = container.querySelector('.list-item-counter');
    expect(counter.getAttribute('aria-hidden')).toBe('true');
  });

  it('deeply nested li gets correct aria-level', () => {
    document.body.innerHTML = `
      <ol>
        <li>L1
          <ol>
            <li>L2
              <ol>
                <li>L3</li>
              </ol>
            </li>
          </ol>
        </li>
      </ol>
    `;
    const list = document.body.querySelector('ol');
    renderList(list, { format: NUMBERING_FORMAT.ARABIC, numberingType: 'injected' });
    const items = document.body.querySelectorAll('li');
    expect(items[2].getAttribute('aria-level')).toBe('3');
  });
});

describe('createListNumberer factory', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('returns ListNumberer instance', () => {
    const html = createListHTML(['A']);
    makeContainer(html);
    const instance = createListNumberer('ol', { autoUpdate: false });
    expect(instance instanceof ListNumberer).toBe(true);
    instance.destroy();
  });
});

describe('getAccessibleLabel', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('sets aria-level on element', () => {
    const html = createListHTML(['Item']);
    makeContainer(html);
    const li = document.querySelector('li');
    getAccessibleLabel(li, '1');
    expect(li.getAttribute('aria-level')).toBeTruthy();
  });
});
