// app.js - Evolução Gamificada V2

// Configuração API
const API_URL = "http://localhost:8000/api";

// Referências DOM
const nodesContainer = document.getElementById('roadmap-nodes');
const lessonPanel = document.getElementById('lesson-panel');
const lessonContent = document.getElementById('lesson-content');
const quizContainer = document.getElementById('quiz-container');
const progressFill = document.getElementById('progress-fill');
const svg = document.getElementById('roadmap-svg');
const view = document.getElementById('roadmap-view');
const roadmapSelector = document.getElementById('roadmap-selector');
const editModeBtn = document.getElementById('edit-mode-btn');
const genQuizBtn = document.getElementById('gen-quiz-btn');

// Estado Global
let currentRoadmap = null;
let currentRoadmapFile = "";
let completedNodes = JSON.parse(localStorage.getItem('completedNodes') || '[]');
let streakData = JSON.parse(localStorage.getItem('streakData') || '{"count": 0, "lastDate": null}');
let currentLessonNode = null;
let isEditMode = false;
let lessonStartTimes = {};
let userXP = parseInt(localStorage.getItem('userXP') || '0');
let depMap = {};  // Cache do mapa de dependências


// Inicialização Mermaid
mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });

// Configuração Marked
const renderer = new marked.Renderer();
renderer.code = (args) => {
    let code = (typeof args === 'object') ? args.text : arguments[0];
    let lang = (typeof args === 'object') ? args.lang : arguments[1];
    if (lang === 'mermaid') return `<div class="mermaid">${code}</div>`;
    return `<pre><code class="language-${lang}">${code}</code></pre>`;
};
marked.setOptions({ renderer });

// --- INICIALIZAÇÃO E CARREGAMENTO ---

async function init() {
    try {
        await loadDepMap();
        await listRoadmaps();
    } catch (e) {
        console.error('Falha na inicialização:', e);
    }
    updateStreakUI();
}

async function loadDepMap() {
    try {
        const response = await fetch(`${API_URL}/dep-map`);
        if (response.ok) {
            depMap = await response.json();
        }
    } catch (e) {
        console.error('Erro ao carregar mapa de dependências:', e);
    }
}

async function listRoadmaps() {
    try {
        const response = await fetch(`${API_URL}/roadmaps`);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status} ${response.statusText}`);
        }
        const files = await response.json();
        if (files.length === 0) {
            roadmapSelector.innerHTML = '<option value="">Nenhum tema encontrado</option>';
            nodesContainer.innerHTML = '<p style="color: red;">Nenhum roadmap disponível. Crie um novo ou verifique o servidor.</p>';
            return;
        }
        roadmapSelector.innerHTML = files.map(f => `<option value="${f}">${f.replace('roadmap_', '').replace('.json', '').toUpperCase()}</option>`).join('');
        // Carrega o primeiro roadmap apenas se houver itens
        loadRoadmap(files[0]);
    } catch (e) {
        console.error('Erro ao listar roadmaps:', e);
        roadmapSelector.innerHTML = '<option value="">Erro ao carregar temas</option>';
        nodesContainer.innerHTML = '<p style="color: red;">Falha ao obter a lista de roadmaps. Verifique o backend.</p>';
    }
}

async function loadRoadmap(filename) {
    if (!filename) {
        currentRoadmap = null;
        nodesContainer.innerHTML = '<p>Selecione um tema no menu acima.</p>';
        return;
    }
    currentRoadmapFile = filename;
    try {
        const response = await fetch(`${API_URL}/roadmap/${filename}`);
        if (!response.ok) {
            throw new Error(`Erro HTTP ao carregar roadmap ${filename}: ${response.status} ${response.statusText}`);
        }
        currentRoadmap = await response.json();
        renderRoadmap();
    } catch (e) {
        console.error('Erro ao carregar roadmap:', e);
        currentRoadmap = null;
        currentRoadmapFile = '';
        nodesContainer.innerHTML = `<p style="color: red;">Falha ao carregar o tema "${filename}". Tente novamente.</p>`;
    }
}

function renderRoadmap() {
    if (!currentRoadmap) return;
    nodesContainer.innerHTML = '';
    const centralNodes = currentRoadmap.nodes.filter(n => n.type === 'central');
    
    centralNodes.forEach(centralNode => {
        if (centralNode.group) {
            const sectionHeader = document.createElement('div');
            sectionHeader.className = 'section-title';
            sectionHeader.innerText = centralNode.group;
            nodesContainer.appendChild(sectionHeader);
        }

        const group = document.createElement('div');
        group.className = 'node-group';

        const childrenContainer = document.createElement('div');
        childrenContainer.className = 'node-children';
        
        const leftCol = document.createElement('div');
        leftCol.className = 'side-column left';
        const rightCol = document.createElement('div');
        rightCol.className = 'side-column right';

        const nodeEl = createNodeElement(centralNode);

        const children = currentRoadmap.nodes.filter(n => centralNode.children && centralNode.children.includes(n.id));
        children.forEach(child => {
            const childEl = createNodeElement(child);
            if (child.side === 'left') leftCol.appendChild(childEl);
            else rightCol.appendChild(childEl);
        });

        childrenContainer.appendChild(leftCol);
        childrenContainer.appendChild(nodeEl);
        childrenContainer.appendChild(rightCol);
        group.appendChild(childrenContainer);
        nodesContainer.appendChild(group);

        const spacer = document.createElement('div');
        spacer.style.height = '120px';
        nodesContainer.appendChild(spacer);
    });
    
    updateProgressBar();
    requestAnimationFrame(() => setTimeout(drawConnections, 300));
}

function createNodeElement(node) {
    const el = document.createElement('div');
    el.className = `node ${node.type} ${completedNodes.includes(node.id) ? 'completed' : ''}`;
    el.id = `node-${node.id}`;
    el.setAttribute('data-difficulty', node.difficulty || 'easy');
    el.innerText = node.title;
    el.onclick = () => showLesson(node);

    // Botões de CRUD (Modo Edição)
    const actions = document.createElement('div');
    actions.className = 'node-actions';
    actions.innerHTML = `
        <button class="node-btn" onclick="event.stopPropagation(); editNode('${node.id}')">✎</button>
        <button class="node-btn delete" onclick="event.stopPropagation(); deleteNode('${node.id}')">✕</button>
    `;
    el.appendChild(actions);

    return el;
}

// --- LIÇÕES E GERAÇÃO IA ---

    async function showLesson(node) {
    // Registro de tempo para XP
    lessonStartTimes[node.id] = Date.now();

    currentLessonNode = node;
    lessonContent.innerHTML = `<p style="color: #888;">Carregando lição de <strong>${node.title}</strong>...</p>`;
    quizContainer.style.display = 'none';
    lessonPanel.classList.add('active');
    
    // Check prerequisites via diagnostic using depMap
    const prereqs = depMap[node.title] || [];
    const hasPrereqs = prereqs.length > 0;
    const isCentralNode = node.type === 'central';
    const parentNode = currentRoadmap?.nodes?.find(n => n.children?.includes(node.id));
    const parentTitle = parentNode?.title || '';
    const parentPrereqs = depMap[parentTitle] || [];
    const parentHasPrereqs = parentPrereqs.length > 0;

    if (isCentralNode || hasPrereqs || parentHasPrereqs) {
        const passed = await runDiagnostic(node);
        if (!passed) {
            return;
        }
    }

    genQuizBtn.style.display = isEditMode ? 'block' : 'none';

    try {
        const response = await fetch(`licoes/${node.id}.md`);
        if (!response.ok) throw new Error('Lição não encontrada.');
        let markdown = await response.text();
        
        const quizMatch = markdown.match(/```json\s*(\[\s*\{[\s\S]*\}\s*\])\s*```/);
        let quizData = null;
        if (quizMatch) {
            try {
                quizData = JSON.parse(quizMatch[1]);
                markdown = markdown.replace(quizMatch[0], '');
            } catch (e) { console.error("Erro Quiz:", e); }
        }

        lessonContent.innerHTML = marked.parse(markdown);
        setTimeout(() => mermaid.run({ nodes: document.querySelectorAll('.mermaid') }), 300);

        if (quizData && !completedNodes.includes(node.id)) {
            renderQuiz(quizData);
        } else if (completedNodes.includes(node.id)) {
            renderCompleteStatus();
        } else {
            renderSimpleComplete(node.id);
        }
    } catch (e) {
        lessonContent.innerHTML = `
            <h2>${node.title}</h2>
            <p>⚠️ Lição ainda não gerada.</p>
            ${isEditMode ? '<p>Clique no botão 🤖 acima para gerar via IA.</p>' : ''}
        `;
    }
}

async function generateLessonForCurrentNode() {
    if (!currentLessonNode) return;
    genQuizBtn.innerText = "⏳ Gerando...";
    genQuizBtn.disabled = true;
    try {
        const response = await fetch(`${API_URL}/generate-lesson`, {
            method: 'POST',
            body: JSON.stringify({
                id: currentLessonNode.id,
                title: currentLessonNode.title,
                type: currentLessonNode.type
            })
        });
        const result = await response.json();
        if (result.status === 'success') showLesson(currentLessonNode);
    } catch (e) {
        alert("Erro ao gerar lição. Verifique o servidor.");
    } finally {
        genQuizBtn.innerText = "🤖 Gerar Lição/Quiz";
        genQuizBtn.disabled = false;
    }
}

// --- CRUD E ROADMAPS ---

window.toggleEditMode = () => {
    isEditMode = !isEditMode;
    document.body.classList.toggle('edit-mode', isEditMode);
    editModeBtn.innerText = isEditMode ? "💾 Sair e Salvar" : "✏️ Modo Edição";
    if (!isEditMode) saveRoadmap();
    if (currentLessonNode) genQuizBtn.style.display = isEditMode ? 'block' : 'none';
};

async function saveRoadmap() {
    if (!currentRoadmap || !currentRoadmapFile) return;
    try {
        await fetch(`${API_URL}/save-roadmap`, {
            method: 'POST',
            body: JSON.stringify({ filename: currentRoadmapFile, data: currentRoadmap })
        });
    } catch (e) { alert("Erro ao salvar no servidor."); }
}

window.deleteNode = (nodeId) => {
    if (!confirm("Remover este tópico?")) return;
    currentRoadmap.nodes = currentRoadmap.nodes.filter(n => n.id !== nodeId);
    // Remove também das listas de children
    currentRoadmap.nodes.forEach(n => {
        if (n.children) n.children = n.children.filter(id => id !== nodeId);
    });
    renderRoadmap();
};

// P2: editNode estava referenciado em createNodeElement mas nunca implementado
window.editNode = (nodeId) => {
    const node = currentRoadmap.nodes.find(n => n.id === nodeId);
    if (!node) return;
    const newTitle = prompt(`Editar título do nó:`, node.title);
    if (newTitle === null) return;
    const trimmed = newTitle.trim();
    if (!trimmed) { alert('O título não pode ser vazio.'); return; }
    node.title = trimmed;
    renderRoadmap();
    saveRoadmap();
};

window.openNewRoadmapModal = () => {
    document.getElementById('modal-overlay').style.display = 'flex';
};

window.closeModal = () => {
    document.getElementById('modal-overlay').style.display = 'none';
};

window.submitGenerateRoadmap = async () => {
    const tema = document.getElementById('new-roadmap-theme').value;
    if (!tema) return;
    
    const btn = document.querySelector('.modal-actions .admin-btn:not(.cancel)');
    btn.innerText = "🧠 Gerando...";
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/generate-roadmap`, {
            method: 'POST',
            body: JSON.stringify({ tema })
        });
        const result = await response.json();
        if (result.status === 'success') {
            await listRoadmaps();
            roadmapSelector.value = result.file;
            loadRoadmap(result.file);
            closeModal();
        }
    } catch (e) { alert("Erro ao gerar roadmap."); }
    finally {
        btn.innerText = "Gerar com IA";
        btn.disabled = false;
    }
};

// --- QUIZ E STREAKS ---

function renderQuiz(questions) {
    quizContainer.innerHTML = '<h3>🧠 Quiz de Validação</h3>';
    quizContainer.style.display = 'block';
    questions.forEach((q, idx) => {
        const qDiv = document.createElement('div');
        qDiv.className = 'quiz-question';
        qDiv.innerHTML = `<p><strong>${idx + 1}. ${q.question}</strong></p>`;
        q.options.forEach((opt, optIdx) => {
            const btn = document.createElement('button');
            btn.className = 'quiz-option';
            btn.innerText = opt;
            btn.onclick = () => {
                const options = qDiv.querySelectorAll('.quiz-option');
                options.forEach(b => b.classList.remove('selected', 'correct', 'wrong'));
                btn.classList.add('selected');
                if (optIdx === q.answer) btn.classList.add('correct');
                else btn.classList.add('wrong');
                checkQuizCompletion(questions);
            };
            qDiv.appendChild(btn);
        });
        quizContainer.appendChild(qDiv);
    });
}

function checkQuizCompletion(questions) {
    const qCount = questions.length;
    // P1: Escopo restrito ao quizContainer atual — evita contagem cruzada entre sessões
    const correctCount = quizContainer.querySelectorAll('.quiz-option.correct.selected').length;
    if (correctCount === qCount) {
        completeNode(currentLessonNode.id);
        renderCompleteStatus();
    }
}

function renderCompleteStatus() {
    quizContainer.innerHTML = `<div class="status-success">🎉 Parabéns! Você dominou este tópico.</div>`;
    quizContainer.style.display = 'block';
}

function renderSimpleComplete(nodeId) {
    quizContainer.innerHTML = `<button class="quiz-submit" onclick="completeNode('${nodeId}')">Marcar como Concluído</button>`;
    quizContainer.style.display = 'block';
}

function completeNode(nodeId) {
    if (!completedNodes.includes(nodeId)) {
        completedNodes.push(nodeId);
        localStorage.setItem('completedNodes', JSON.stringify(completedNodes));
        // XP reward if completed within 15min
        const start = lessonStartTimes[nodeId];
        if (start && Date.now() - start <= 15 * 60 * 1000) {
            userXP += 10;
            localStorage.setItem('userXP', userXP);
            alert(`💎 +10 XP! Total: ${userXP}`);
        }
        updateStreak();
        renderRoadmap();
        updateProgressBar();
    }
}

// --- CONEXÕES SVG ---

function getAbsoluteCoords(el) {
    let top = 0, left = 0;
    let curr = el;
    while (curr && curr !== view) {
        top += curr.offsetTop || 0;
        left += curr.offsetLeft || 0;
        curr = curr.offsetParent;
    }
    return { x: left + el.offsetWidth / 2, y: top + el.offsetHeight / 2 };
}

function drawConnections() {
    if (!currentRoadmap) return;
    svg.innerHTML = '';
    svg.setAttribute('height', view.scrollHeight);
    svg.setAttribute('width', view.scrollWidth);
    const centralNodes = currentRoadmap.nodes.filter(n => n.type === 'central');
    centralNodes.forEach((cn, idx) => {
        const pEl = document.getElementById(`node-${cn.id}`);
        if (!pEl) return;
        const pC = getAbsoluteCoords(pEl);
        if (cn.children) {
            cn.children.forEach(cid => {
                const cEl = document.getElementById(`node-${cid}`);
                if (!cEl) return;
                const cC = getAbsoluteCoords(cEl);
                drawBezier(pC.x, pC.y, cC.x, cC.y);
            });
        }
        if (idx < centralNodes.length - 1) {
            const nextEl = document.getElementById(`node-${centralNodes[idx+1].id}`);
            if (nextEl) {
                const nC = getAbsoluteCoords(nextEl);
                drawLine(pC.x, pC.y, nC.x, nC.y, true);
            }
        }
    });
}

function drawBezier(x1, y1, x2, y2) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const controlY = y1 + (y2 - y1) / 2;
    path.setAttribute('d', `M ${x1} ${y1} C ${x1} ${controlY}, ${x2} ${controlY}, ${x2} ${y2}`);
    path.setAttribute('class', 'roadmap-path');
    svg.appendChild(path);
}

function drawLine(x1, y1, x2, y2, isSpine = false) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M ${x1} ${y1} L ${x2} ${y2}`);
    path.setAttribute('class', `roadmap-path ${isSpine ? 'spine-line' : ''}`);
    svg.appendChild(path);
}

// --- UTILITÁRIOS ---

function updateProgressBar() {
    if (!currentRoadmap) return;
    const total = currentRoadmap.nodes.length;
    // P1: Filtra apenas os nós do roadmap atual, evitando contagem cruzada entre roadmaps
    const completed = completedNodes.filter(id =>
        currentRoadmap.nodes.some(n => n.id === id)
    ).length;
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
    if (progressFill) progressFill.style.width = `${pct}%`;
    const pctEl = document.getElementById('progress-percent');
    if (pctEl) pctEl.innerText = `${pct}%`;
}

function updateStreak() {
    const today = new Date().toISOString().split('T')[0];
    if (streakData.lastDate === today) return;
    const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
    const yStr = yesterday.toISOString().split('T')[0];
    if (streakData.lastDate === yStr) streakData.count++;
    else streakData.count = 1;
    streakData.lastDate = today;
    localStorage.setItem('streakData', JSON.stringify(streakData));
    updateStreakUI();
}

function updateStreakUI() {
    const el = document.getElementById('streak-days');
    if (el) el.innerText = streakData.count;
}

// --- DIAGNÓSTICO DE LACUNAS ---

async function runDiagnostic(node) {
    try {
        // Show loading state
        lessonContent.innerHTML = `<p style="color: #888;">Executando diagnóstico de <strong>${node.title}</strong>...</p>`;
        
        // Get user's self-assessment (in a real app, this could be more sophisticated)
        // For now, we'll use a simple prompt asking the user to explain the concept
        const userAnswer = prompt(
            `Para acessar "${node.title}", por favor explique brevemente o que você sabe sobre este tópico:\n\nSeja específico sobre fórmulas, regras ou conceitos-chave que você entende.`
        );
        
        if (userAnswer === null) {
            // User cancelled
            return false;
        }
        
        if (!userAnswer.trim()) {
            alert('Por favor, forneça uma resposta para continuar com o diagnóstico.');
            return false;
        }
        
        // Call diagnostic API
        const response = await fetch(`${API_URL}/diagnose`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: node.title,
                user_answer: userAnswer
            })
        });
        
        if (!response.ok) {
            throw new Error(`Erro no diagnóstico: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === "error") {
            throw new Error(result.message || 'Erro desconhecido no diagnóstico');
        }
        
        // Show result to user
        const hasGap = result.has_gap || result.status === "miss";
        
        if (hasGap) {
            // Show review modal with the diagnosis - user needs to review before proceeding
            showReviewModal({
                title: `Revisão necessária: ${node.title}`,
                message: result.message,
                tags: result.tags || [],
                showRetryButton: true,  // User can retry after reviewing
                onRetry: () => {
                    // Close modal and retry diagnostic
                    closeModal();
                    setTimeout(() => runDiagnostic(node), 100);
                },
                onClose: () => {
                    // User closed without retry - stay on current lesson
                    return false;
                }
            });
            return false; // Block access for now
        } else {
            // Show success message and grant access
            showReviewModal({
                title: `Acesso liberado: ${node.title}`,
                message: result.message,
                tags: result.tags || [],
                onClose: () => true
            });
            return true; // Grant access
        }
    } catch (error) {
        console.error('Erro no diagnóstico:', error);
        // In case of error, allow access to avoid blocking the user
        alert('Não foi possível executar o diagnóstico. Permitindo acesso como medida de segurança.');
        return true;
    }
}

function showReviewModal(data) {
    const overlay = document.createElement('div');
    overlay.className = 'review-modal-overlay';

    const modal = document.createElement('div');
    modal.className = 'review-modal';

    // Header
    const header = document.createElement('div');
    header.className = 'review-modal-header';
    const h3 = document.createElement('h3');
    // P0: textContent em vez de innerHTML — previne XSS com dados do LLM
    h3.textContent = data.title;
    const closeBtn = document.createElement('button');
    closeBtn.className = 'review-modal-close';
    closeBtn.textContent = '×';
    closeBtn.onclick = () => overlay.remove();
    header.appendChild(h3);
    header.appendChild(closeBtn);

    // Body
    const body = document.createElement('div');
    body.className = 'review-modal-body';
    const msgP = document.createElement('p');
    msgP.textContent = data.message;
    body.appendChild(msgP);

    if (data.tags && data.tags.length > 0) {
        const tagsDiv = document.createElement('div');
        tagsDiv.className = 'review-modal-tags';
        const label = document.createElement('strong');
        label.textContent = 'Pré-requisitos relacionados: ';
        tagsDiv.appendChild(label);
        data.tags.forEach(tag => {
            const span = document.createElement('span');
            span.className = 'tag';
            span.textContent = tag;
            tagsDiv.appendChild(span);
        });
        body.appendChild(tagsDiv);
    }

    // Footer
    const footer = document.createElement('div');
    footer.className = 'review-modal-footer';

    if (data.showRetryButton) {
        const retryBtn = document.createElement('button');
        retryBtn.className = 'review-modal-btn retry-btn';
        retryBtn.textContent = 'Tentar novamente';
        retryBtn.onclick = () => {
            overlay.remove();
            if (typeof data.onRetry === 'function') data.onRetry();
        };
        footer.appendChild(retryBtn);
    }

    const closeActionBtn = document.createElement('button');
    closeActionBtn.className = 'review-modal-btn';
    closeActionBtn.textContent = typeof data.onClose === 'function' ? 'Revisar novamente' : 'Entendi, continuar';
    closeActionBtn.onclick = () => {
        overlay.remove();
        if (typeof data.onClose === 'function') data.onClose();
    };
    footer.appendChild(closeActionBtn);

    modal.appendChild(header);
    modal.appendChild(body);
    modal.appendChild(footer);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

window.toggleZenMode = () => document.body.classList.toggle('zen-mode');
window.closePanel = () => {
    lessonPanel.classList.remove('active');
    document.body.classList.remove('zen-mode');
};

document.addEventListener('DOMContentLoaded', init);
// P1: Removido setInterval(drawConnections, 5000) — causava layout thrashing periódico
// drawConnections é chamado apenas após eventos reais (resize, render)
window.addEventListener('resize', () => requestAnimationFrame(drawConnections));

window.loadRoadmap = loadRoadmap;
window.generateLessonForCurrentNode = generateLessonForCurrentNode;
window.regenerateDepMap = async () => {
    try {
        const response = await fetch(`${API_URL}/regenerate-dep-map`, { method: 'POST' });
        const result = await response.json();
        if (result.status === 'success') {
            await loadDepMap();
            alert(`Mapa de dependências atualizado! (${result.entries} entradas)`);
        }
    } catch (e) {
        alert('Erro ao atualizar mapa de dependências.');
    }
};
