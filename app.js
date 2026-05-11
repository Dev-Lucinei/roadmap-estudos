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
    if (!currentRoadmap) {
        console.error('renderRoadmap: currentRoadmap é null');
        return;
    }
    
    console.log('renderRoadmap: Iniciando renderização', currentRoadmap);
    
    // Usar apenas layout de fluxograma
    const flowchartContainer = document.getElementById('flowchart-container');
    const nodesContainer = document.getElementById('roadmap-nodes');
    
    if (!flowchartContainer) {
        console.error('renderRoadmap: flowchart-container não encontrado');
        return;
    }
    
    // Ocultar container antigo, mostrar fluxograma
    nodesContainer.style.display = 'none';
    flowchartContainer.style.display = 'block';
    
    // Verificar se FlowchartLayout está disponível
    if (typeof FlowchartLayout === 'undefined') {
        console.error('renderRoadmap: FlowchartLayout não está definido');
        flowchartContainer.innerHTML = '<p style="color: red; padding: 40px; text-align: center;">Erro: FlowchartLayout não carregado. Verifique se flowchart_layout.js está incluído.</p>';
        return;
    }
    
    // Inicializar flowchart se necessário
    if (!window.flowchartInstance) {
        console.log('renderRoadmap: Criando nova instância de FlowchartLayout');
        window.flowchartInstance = new FlowchartLayout('flowchart-container', 'flowchart-svg');
    }
    
    // Renderizar
    console.log('renderRoadmap: Chamando render()');
    window.flowchartInstance.render(currentRoadmap);
    
    // Marcar nós completos
    setTimeout(() => {
        completedNodes.forEach(nodeId => {
            const nodeEl = document.getElementById(`node-${nodeId}`);
            if (nodeEl) nodeEl.classList.add('completed');
        });
    }, 100);
    
    updateProgressBar();
    console.log('renderRoadmap: Renderização concluída');
}

function createNodeElement(node, level = 0) {
    const hasSubtopics = node.subtopics && node.subtopics.length > 0;
    
    // Wrapper para o nó e seus subtópicos
    const wrapper = document.createElement('div');
    wrapper.className = 'node-wrapper';
    wrapper.id = `wrapper-${node.id}`;
    wrapper.setAttribute('data-level', level);
    
    const el = document.createElement('div');
    el.className = `node ${node.type || 'topic'} ${completedNodes.includes(node.id) ? 'completed' : ''} ${hasSubtopics ? 'has-children' : ''}`;
    el.id = `node-${node.id}`;
    el.setAttribute('data-difficulty', node.difficulty || 'easy');
    
    const titleSpan = document.createElement('span');
    titleSpan.className = 'node-title';
    titleSpan.innerText = node.title;
    el.appendChild(titleSpan);

    // Ícone de expansão se houver subtópicos
    if (hasSubtopics) {
        const expandIcon = document.createElement('span');
        expandIcon.className = 'node-expand-icon';
        expandIcon.innerText = '›';
        el.appendChild(expandIcon);
        
        el.onclick = (e) => {
            e.stopPropagation();
            console.log('Click no nó:', node.id, 'Level:', level);
            toggleSubtopics(node.id);
        };
    } else {
        // Se não tem subtópicos, abre a lição
        el.onclick = () => showLesson(node);
    }

    // Botões de CRUD (Modo Edição)
    const actions = document.createElement('div');
    actions.className = 'node-actions';
    actions.innerHTML = `
        <button class="node-btn" onclick="event.stopPropagation(); editNode('${node.id}')">✎</button>
        <button class="node-btn delete" onclick="event.stopPropagation(); deleteNode('${node.id}')">✕</button>
    `;
    el.appendChild(actions);

    wrapper.appendChild(el);

    // Container de subtópicos em árvore (RECURSIVO)
    if (hasSubtopics) {
        const subtopicsContainer = document.createElement('div');
        subtopicsContainer.className = 'node-subtopics-tree';
        subtopicsContainer.id = `subtopics-${node.id}`;
        
        node.subtopics.forEach((subtopic) => {
            // Cria objeto completo para o subtópico
            const subtopicNode = {
                id: subtopic.id || `${node.id}_${subtopic.title}`,
                title: subtopic.title || subtopic,
                subtopics: subtopic.subtopics || [],
                type: 'subtopic',
                difficulty: subtopic.difficulty || node.difficulty
            };
            
            // RECURSÃO: cria elemento para o subtópico (que pode ter seus próprios subtópicos)
            const subtopicWrapper = createNodeElement(subtopicNode, level + 1);
            subtopicsContainer.appendChild(subtopicWrapper);
        });
        
        wrapper.appendChild(subtopicsContainer);
    }

    return wrapper;
}

function toggleSubtopics(nodeId) {
    const wrapper = document.getElementById(`wrapper-${nodeId}`);
    const nodeEl = document.getElementById(`node-${nodeId}`);
    const subtopicsEl = document.getElementById(`subtopics-${nodeId}`);
    
    console.log('Toggle subtopics:', nodeId);
    console.log('Wrapper:', wrapper);
    console.log('Node:', nodeEl);
    console.log('Subtopics:', subtopicsEl);
    
    if (!wrapper || !nodeEl || !subtopicsEl) {
        console.error('Elementos não encontrados!');
        return;
    }
    
    const isExpanded = wrapper.classList.contains('expanded');
    console.log('Is expanded:', isExpanded);
    
    if (isExpanded) {
        wrapper.classList.remove('expanded');
        nodeEl.classList.remove('expanded');
    } else {
        wrapper.classList.add('expanded');
        nodeEl.classList.add('expanded');
    }
    
    console.log('Classes após toggle:', wrapper.className);
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
    return new Promise((resolve) => {
        showDiagnosticModal(node, resolve);
    });
}

function showDiagnosticModal(node, onComplete) {
    const overlay = document.createElement('div');
    overlay.className = 'diagnostic-modal-overlay';

    const modal = document.createElement('div');
    modal.className = 'diagnostic-modal';

    // Header
    const header = document.createElement('div');
    header.className = 'diagnostic-modal-header';
    const h3 = document.createElement('h3');
    h3.textContent = `Avaliação: ${node.title}`;
    header.appendChild(h3);

    // Body
    const body = document.createElement('div');
    body.className = 'diagnostic-modal-body';

    // Tabs
    const tabs = document.createElement('div');
    tabs.className = 'diagnostic-tabs';
    tabs.innerHTML = `
        <button class="diagnostic-tab active" data-tab="checklist">📋 Auto-avaliação</button>
        <button class="diagnostic-tab" data-tab="quiz">🧠 Quiz IA</button>
    `;

    // Tab contents
    const tabContents = document.createElement('div');
    tabContents.className = 'diagnostic-tab-contents';

    // Checklist tab
    const checklistTab = document.createElement('div');
    checklistTab.className = 'diagnostic-tab-content active';
    checklistTab.id = 'tab-checklist';
    checklistTab.innerHTML = `
        <p class="diagnostic-intro">Marque os itens que você domina sobre <strong>${node.title}</strong>:</p>
        <div id="checklist-items"></div>
        <div class="diagnostic-actions">
            <button class="diagnostic-btn secondary" onclick="this.closest('.diagnostic-modal-overlay').remove()">Cancelar</button>
            <button class="diagnostic-btn primary" id="checklist-submit">Avaliar</button>
        </div>
    `;

    // Quiz tab
    const quizTab = document.createElement('div');
    quizTab.className = 'diagnostic-tab-content';
    quizTab.id = 'tab-quiz';
    quizTab.innerHTML = `
        <p class="diagnostic-intro">Responda às perguntas geradas pela IA sobre <strong>${node.title}</strong>:</p>
        <div id="quiz-generation">
            <button class="diagnostic-btn primary" id="generate-quiz-btn">🤖 Gerar Quiz</button>
        </div>
        <div id="quiz-questions" style="display: none;"></div>
        <div id="quiz-actions" style="display: none;" class="diagnostic-actions">
            <button class="diagnostic-btn secondary" onclick="this.closest('.diagnostic-modal-overlay').remove()">Cancelar</button>
            <button class="diagnostic-btn primary" id="quiz-submit">Enviar Respostas</button>
        </div>
    `;

    tabContents.appendChild(checklistTab);
    tabContents.appendChild(quizTab);
    body.appendChild(tabs);
    body.appendChild(tabContents);

    modal.appendChild(header);
    modal.appendChild(body);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Tab switching
    tabs.querySelectorAll('.diagnostic-tab').forEach(tab => {
        tab.onclick = () => {
            tabs.querySelectorAll('.diagnostic-tab').forEach(t => t.classList.remove('active'));
            tabContents.querySelectorAll('.diagnostic-tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
        };
    });

    // Load checklist items
    loadChecklistItems(node);

    // Checklist submit
    document.getElementById('checklist-submit').onclick = async () => {
        const result = await evaluateChecklist(node);
        overlay.remove();
        onComplete(result.passed);
    };

    // Quiz generation
    document.getElementById('generate-quiz-btn').onclick = async () => {
        await generateDiagnosticQuiz(node);
    };

    // Quiz submit
    document.getElementById('quiz-submit').onclick = async () => {
        const result = await evaluateQuizAnswers(node);
        overlay.remove();
        onComplete(result.passed);
    };
}

async function loadChecklistItems(node) {
    const container = document.getElementById('checklist-items');
    container.innerHTML = '<p style="color: #888;">Carregando checklist...</p>';

    try {
        const response = await fetch(`${API_URL}/generate-checklist`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: node.title })
        });

        if (!response.ok) throw new Error('Falha ao gerar checklist');

        const data = await response.json();
        const items = data.items || [];

        container.innerHTML = '';
        items.forEach((item, idx) => {
            const div = document.createElement('div');
            div.className = 'checklist-item';
            div.innerHTML = `
                <input type="checkbox" id="check-${idx}" />
                <label for="check-${idx}">${item}</label>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Erro ao carregar checklist:', error);
        container.innerHTML = '<p style="color: red;">Erro ao carregar checklist. Tente o Quiz IA.</p>';
    }
}

async function evaluateChecklist(node) {
    const checkboxes = document.querySelectorAll('#checklist-items input[type="checkbox"]');
    const total = checkboxes.length;
    const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
    const percentage = total > 0 ? (checked / total) * 100 : 0;

    const passed = percentage >= 70;

    showResultModal({
        title: passed ? '✅ Aprovado!' : '⚠️ Revisão Recomendada',
        message: passed 
            ? `Você marcou ${checked}/${total} itens (${percentage.toFixed(0)}%). Pode prosseguir!`
            : `Você marcou apenas ${checked}/${total} itens (${percentage.toFixed(0)}%). Recomendamos revisar o conteúdo antes de avançar.`,
        passed: passed,
        topic: node.title
    });

    return { passed };
}

async function generateDiagnosticQuiz(node) {
    const btn = document.getElementById('generate-quiz-btn');
    const container = document.getElementById('quiz-questions');
    const actions = document.getElementById('quiz-actions');

    btn.disabled = true;
    btn.textContent = '⏳ Gerando...';

    try {
        const response = await fetch(`${API_URL}/generate-diagnostic-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: node.title })
        });

        if (!response.ok) throw new Error('Falha ao gerar quiz');

        const data = await response.json();
        const questions = data.questions || [];

        container.innerHTML = '';
        questions.forEach((q, idx) => {
            const div = document.createElement('div');
            div.className = 'quiz-question-diagnostic';
            div.innerHTML = `
                <p class="question-text"><strong>${idx + 1}.</strong> ${q.question}</p>
                <textarea 
                    id="answer-${idx}" 
                    class="quiz-answer-input" 
                    placeholder="Digite sua resposta aqui..."
                    maxlength="500"
                ></textarea>
                <small class="char-count">0/500 caracteres</small>
            `;
            container.appendChild(div);

            // Character counter
            const textarea = div.querySelector('textarea');
            const counter = div.querySelector('.char-count');
            textarea.oninput = () => {
                counter.textContent = `${textarea.value.length}/500 caracteres`;
            };
        });

        document.getElementById('quiz-generation').style.display = 'none';
        container.style.display = 'block';
        actions.style.display = 'flex';
    } catch (error) {
        console.error('Erro ao gerar quiz:', error);
        alert('Erro ao gerar quiz. Tente novamente ou use a auto-avaliação.');
    } finally {
        btn.disabled = false;
        btn.textContent = '🤖 Gerar Quiz';
    }
}

async function evaluateQuizAnswers(node) {
    const textareas = document.querySelectorAll('.quiz-answer-input');
    const answers = Array.from(textareas).map(ta => ta.value.trim());

    // Validação: todas as respostas devem estar preenchidas
    if (answers.some(a => !a)) {
        alert('Por favor, responda todas as perguntas antes de enviar.');
        return { passed: false };
    }

    const submitBtn = document.getElementById('quiz-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Avaliando...';

    try {
        const response = await fetch(`${API_URL}/evaluate-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: node.title,
                answers: answers
            })
        });

        if (!response.ok) throw new Error('Falha ao avaliar respostas');

        const result = await response.json();

        showResultModal({
            title: result.passed ? '✅ Aprovado!' : '⚠️ Revisão Recomendada',
            message: result.feedback,
            passed: result.passed,
            topic: node.title,
            score: result.score
        });

        return { passed: result.passed };
    } catch (error) {
        console.error('Erro ao avaliar quiz:', error);
        alert('Erro ao avaliar respostas. Permitindo acesso por segurança.');
        return { passed: true };
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enviar Respostas';
    }
}

function showResultModal(data) {
    const overlay = document.createElement('div');
    overlay.className = 'result-modal-overlay';

    const modal = document.createElement('div');
    modal.className = 'result-modal';

    const icon = data.passed ? '✅' : '⚠️';
    const color = data.passed ? '#4caf50' : '#ff9800';

    modal.innerHTML = `
        <div class="result-modal-header" style="background: ${color};">
            <span class="result-icon">${icon}</span>
            <h3>${data.title}</h3>
        </div>
        <div class="result-modal-body">
            <p>${data.message}</p>
            ${data.score ? `<p class="result-score">Pontuação: ${data.score}%</p>` : ''}
            ${!data.passed ? `<p class="result-tip">💡 Dica: Revise o conteúdo de <strong>${data.topic}</strong> antes de avançar.</p>` : ''}
        </div>
        <div class="result-modal-footer">
            <button class="diagnostic-btn primary" onclick="this.closest('.result-modal-overlay').remove()">
                ${data.passed ? 'Continuar' : 'Entendi'}
            </button>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

// Função removida - substituída por showResultModal

window.toggleZenMode = () => document.body.classList.toggle('zen-mode');
window.closePanel = () => {
    lessonPanel.classList.remove('active');
    document.body.classList.remove('zen-mode');
};

// --- ALTERNÂNCIA DE LAYOUT ---

// Integrar flowchart com showLesson
if (typeof FlowchartLayout !== 'undefined') {
    FlowchartLayout.prototype.onNodeClick = function(node) {
        showLesson(node);
    };
}

// Funções de controle de expansão
function expandAllNodes() {
    if (!window.flowchartInstance || !currentRoadmap) return;
    
    // Expandir todos os nós que têm subtópicos
    currentRoadmap.nodes.forEach(node => {
        if (node.subtopics && node.subtopics.length > 0) {
            window.flowchartInstance.expandedNodes.add(node.id);
            node.subtopics.forEach(sub => {
                if (sub.subtopics && sub.subtopics.length > 0) {
                    window.flowchartInstance.expandedNodes.add(sub.id);
                }
            });
        }
    });
    
    window.flowchartInstance.render(currentRoadmap);
    
    // Re-aplicar nós completos
    setTimeout(() => {
        completedNodes.forEach(nodeId => {
            const nodeEl = document.getElementById(`node-${nodeId}`);
            if (nodeEl) nodeEl.classList.add('completed');
        });
    }, 100);
}

function collapseAllNodes() {
    if (!window.flowchartInstance || !currentRoadmap) return;
    
    window.flowchartInstance.expandedNodes.clear();
    window.flowchartInstance.render(currentRoadmap);
    
    // Re-aplicar nós completos
    setTimeout(() => {
        completedNodes.forEach(nodeId => {
            const nodeEl = document.getElementById(`node-${nodeId}`);
            if (nodeEl) nodeEl.classList.add('completed');
        });
    }, 100);
}

document.addEventListener('DOMContentLoaded', init);
// P1: Removido setInterval(drawConnections, 5000) — causava layout thrashing periódico
// drawConnections é chamado apenas após eventos reais (resize, render)
window.addEventListener('resize', () => requestAnimationFrame(drawConnections));

window.loadRoadmap = loadRoadmap;
window.expandAllNodes = expandAllNodes;
window.collapseAllNodes = collapseAllNodes;
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
