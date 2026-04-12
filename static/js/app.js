/**
 * Клиентская логика лендинга MedTech AI:
 * cookies + API, калькулятор ROI, квиз диагностики потенциала, график Chart.js, раскрытие кейсов.
 */
(function () {
  'use strict';

  /** CSRF-токен из meta (Flask-WTF). */
  function getCsrfToken() {
    var m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.getAttribute('content') || '' : '';
  }

  /** Плашка cookies: запись в БД через API и скрытие через localStorage. */
  function initCookieBanner() {
    var storageKey = 'siteCookiesAccepted';
    var banner = document.getElementById('cookie-banner');
    var btn = document.getElementById('cookie-accept');
    if (!banner || !btn) return;

    function setBottomPadding(show) {
      document.body.style.paddingBottom = show ? '5.5rem' : '';
    }

    function hideBanner() {
      banner.classList.add('hidden');
      setBottomPadding(false);
    }

    try {
      if (localStorage.getItem(storageKey)) {
        hideBanner();
        return;
      }
    } catch (e) {
      /* localStorage недоступен — только показ баннера */
    }

    banner.classList.remove('hidden');
    setBottomPadding(true);

    btn.addEventListener('click', function () {
      var url = window.APP_URLS && window.APP_URLS.cookieConsent;
      if (url) {
        fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: '{}',
        }).catch(function () {});
      }
      try {
        localStorage.setItem(storageKey, '1');
      } catch (e) {}
      hideBanner();
    });
  }

  /** ROI: 15 минут × запросы/день × 30 дней → часы в месяц. */
  function initRoiCalculator() {
    var input = document.getElementById('roi-requests');
    var valEl = document.getElementById('roi-requests-value');
    var hoursEl = document.getElementById('roi-hours');
    if (!input || !valEl || !hoursEl) return;

    var DAYS = 30;
    var MIN_PER_REQUEST = 15;

    function formatHours(h) {
      var rounded = Math.round(h * 10) / 10;
      if (rounded % 1 === 0) return String(Math.round(rounded));
      return String(rounded).replace('.', ',');
    }

    function update() {
      var n = parseInt(input.value, 10);
      if (isNaN(n)) return;
      valEl.textContent = String(n);
      hoursEl.textContent = formatHours((n * MIN_PER_REQUEST * DAYS) / 60);
    }

    input.addEventListener('input', update);
    update();
  }

  /**
   * Раскрытие полного текста кейса: класс .is-open на .case-panel
   * (CSS grid 0fr → 1fr в шаблоне, без динамических классов Tailwind).
   */
  function initCaseAccordions() {
    document.querySelectorAll('.case-toggle').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var card = btn.closest('[data-case]');
        if (!card) return;
        var panel = card.querySelector('[data-case-panel]');
        if (!panel) return;
        var expanded = btn.getAttribute('aria-expanded') === 'true';
        if (expanded) {
          panel.classList.remove('is-open');
          panel.setAttribute('aria-hidden', 'true');
          btn.setAttribute('aria-expanded', 'false');
          btn.textContent = 'Подробнее';
        } else {
          panel.classList.add('is-open');
          panel.setAttribute('aria-hidden', 'false');
          btn.setAttribute('aria-expanded', 'true');
          btn.textContent = 'Свернуть';
        }
      });
    });
  }

  var auditChartInstance = null;

  /** Пошаговый квиз диагностики, сохранение результата, столбчатый график. */
  function initAiCheckup() {
    var root = document.getElementById('quiz-root');
    if (!root) return;

    var steps = [
      document.getElementById('quiz-step-1'),
      document.getElementById('quiz-step-2'),
      document.getElementById('quiz-step-3'),
    ];
    var resultEl = document.getElementById('quiz-result');
    if (!steps[0] || !resultEl) return;

    function showStepIndex(index) {
      steps.forEach(function (el, i) {
        if (!el) return;
        el.classList.toggle('hidden', i !== index);
      });
    }

    function getRadioValue(name) {
      var el = root.querySelector('input[name="' + name + '"]:checked');
      return el ? parseInt(el.value, 10) : null;
    }

    root.querySelectorAll('.quiz-next').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var stepEl = btn.closest('.quiz-step');
        if (!stepEl) return;
        var stepNum = parseInt(stepEl.getAttribute('data-step'), 10);
        var qName = 'q' + stepNum;
        if (getRadioValue(qName) === null) {
          window.alert('Выберите вариант ответа.');
          return;
        }
        if (stepNum < 3) {
          showStepIndex(stepNum);
        }
      });
    });

    root.querySelectorAll('.quiz-prev').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var stepEl = btn.closest('.quiz-step');
        if (!stepEl) return;
        var stepNum = parseInt(stepEl.getAttribute('data-step'), 10);
        showStepIndex(stepNum - 2);
      });
    });

    var finishBtn = document.getElementById('quiz-finish');
    if (finishBtn) {
      finishBtn.addEventListener('click', function () {
        if (getRadioValue('q3') === null) {
          window.alert('Выберите вариант ответа.');
          return;
        }
        var q1 = getRadioValue('q1');
        var q2 = getRadioValue('q2');
        var q3 = getRadioValue('q3');
        var score = 60;

        var auditUrl = window.APP_URLS && window.APP_URLS.audit;
        if (auditUrl) {
          fetch(auditUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ q1: q1, q2: q2, q3: q3 }),
          })
            .then(function (r) {
              return r.json();
            })
            .then(function (data) {
              if (data && data.ok && typeof data.score === 'number') {
                score = data.score;
              }
              renderQuizResult(score);
            })
            .catch(function () {
              renderQuizResult(score);
            });
        } else {
          renderQuizResult(score);
        }
      });
    }

    /** Рекомендация по шкале готовности (экспертная формулировка под отрасль). */
    function recommendedStrategy(s) {
      if (s < 55) {
        return 'начать с аудита процессов и пилотного сценария на ограниченном объёме данных, зафиксировать KPI и по результатам масштабировать решение.';
      }
      if (s < 72) {
        return 'структурировать базу знаний, внедрить AI-ассистента в приоритетный канал коммуникаций и связать ответы с CRM/ERP для сквозной аналитики.';
      }
      if (s < 88) {
        return 'расширить покрытие ассистента на смежные подразделения, внедрить мониторинг качества ответов и режим непрерывного дообучения.';
      }
      return 'перейти к полномасштабной оптимизации: сквозные сценарии, углублённые интеграции и выделенный контур сопровождения модели.';
    }

    function renderQuizResult(score) {
      steps.forEach(function (el) {
        if (el) el.classList.add('hidden');
      });
      resultEl.classList.remove('hidden');

      var expert = document.getElementById('audit-expert-text');
      if (expert) {
        /* Цвет #008080 инлайном: CDN Tailwind не подхватывает классы из innerHTML. */
        expert.innerHTML =
          'Ваш уровень готовности к внедрению ИИ: <strong style="color:#008080;font-weight:700">' +
          score +
          '%</strong>. Рекомендуемая стратегия: ' +
          recommendedStrategy(score);
      }

      var chartWrap = document.getElementById('audit-chart-wrap');
      var cta = document.getElementById('plan-cta');
      if (chartWrap) {
        chartWrap.classList.remove('is-visible');
      }
      if (cta) {
        cta.classList.remove('is-visible');
      }

      var canvas = document.getElementById('audit-chart');
      if (canvas && typeof Chart !== 'undefined') {
        if (auditChartInstance) {
          auditChartInstance.destroy();
        }
        var ctx = canvas.getContext('2d');
        var reserve = Math.max(10, Math.min(90, 100 - score));
        auditChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Запас по процессам (усл.)', 'Потенциал автоматизации'],
            datasets: [
              {
                data: [reserve, score],
                backgroundColor: ['#cbd5e1', '#008080'],
                borderRadius: 8,
              },
            ],
          },
          options: {
            responsive: true,
            animation: {
              duration: 900,
              easing: 'easeOutQuart',
            },
            plugins: {
              legend: { display: false },
              tooltip: { enabled: true },
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                ticks: { callback: function (v) { return v + '%'; } },
              },
            },
          },
        });
      }

      /* Плавное «выплывание» блока с графиком и кнопки CTA после отрисовки. */
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          if (chartWrap) {
            chartWrap.classList.add('is-visible');
          }
          window.setTimeout(function () {
            if (cta) {
              cta.classList.add('is-visible');
            }
          }, 120);
        });
      });

      if (cta && !cta.getAttribute('data-focus-bound')) {
        cta.setAttribute('data-focus-bound', '1');
        cta.addEventListener(
          'click',
          function () {
            window.requestAnimationFrame(function () {
              var nameInput = document.querySelector('#contact input[name="name"]');
              if (nameInput) nameInput.focus();
            });
          },
          { passive: true }
        );
      }
    }

    showStepIndex(0);
  }

  document.addEventListener('DOMContentLoaded', function () {
    initCookieBanner();
    initRoiCalculator();
    initCaseAccordions();
    initAiCheckup();
  });
})();
