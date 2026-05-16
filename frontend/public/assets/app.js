// app.js - Evolução Gamificada V2

// Configuração API
const API_URL = "http://localhost:8000/api";

// Mobile detection
function isMobile() {
    return window.innerWidth <= 768;
}

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
const generateLessonBtn = document.getElementById('generate-lesson-btn');
const generateQuizBtn = document.getElementById('generate-quiz-btn');

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
let currentQuizData = null;  // Armazena o quiz gerado


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
            nodesContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🗺️</div>
                    <div class="empty-state-title">Nenhum roadmap encontrado</div>
                    <div class="empty-state-description">Crie seu primeiro roadmap de estudos com IA. Escolha um tema como "DevOps", "React" ou "Data Science".</div>
                    <button class="empty-state-action" onclick="openNewRoadmapModal()">Criar Roadmap</button>
                </div>
            `;
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
    console.log('renderRoadmap: Chamando init()');
    window.flowchartInstance.init(currentRoadmap);
    
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
    showLoadingSkeleton(lessonContent);
    quizContainer.style.display = 'none';
    lessonPanel.classList.add('active');
    lessonPanel.setAttribute('aria-hidden', 'false');
    const firstFocusable = lessonPanel.querySelector('button, [tabindex]:not([tabindex="-1"])');
    if (firstFocusable) setTimeout(() => firstFocusable.focus(), 100);
    
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

    try {
        const response = await fetch(`licoes/${node.id}.md`);
        if (!response.ok) throw new Error('Lição não encontrada.');
        let markdown = await response.text();
        
        lessonContent.innerHTML = marked.parse(markdown);
        setTimeout(() => mermaid.run({ nodes: document.querySelectorAll('.mermaid') }), 300);

        if (completedNodes.includes(node.id)) {
            renderCompleteStatus();
        } else {
            renderSimpleComplete(node.id);
        }
    } catch (e) {
        lessonContent.innerHTML = `
            <h2>${node.title}</h2>
            <p>⚠️ Lição ainda não gerada.</p>
            <p>Clique no botão <strong>📝 Gerar Conteúdo</strong> acima para criar a lição via IA.</p>
        `;
    }
}

async function generateLessonContent() {
    if (!currentLessonNode) {
        alert('Nenhuma lição selecionada.');
        return;
    }

    console.log('[DEBUG] Iniciando geração de lição para:', currentLessonNode);

    const btn = document.getElementById('generate-lesson-btn');
    if (!btn) {
        console.error('[ERROR] Botão generate-lesson-btn não encontrado!');
        alert('Erro: Botão não encontrado na interface.');
        return;
    }

    const originalText = btn.innerText;
    btn.innerText = "⏳ Gerando conteúdo...";
    btn.disabled = true;

    // Exibe estado de loading no painel
    lessonContent.innerHTML = `
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 3rem; margin-bottom: 20px;">🧠</div>
            <h2>Gerando conteúdo da lição...</h2>
            <p style="color: #888;">A IA está criando conteúdo exclusivo para <strong>${currentLessonNode.title}</strong></p>
            <div class="loading-spinner"></div>
        </div>
    `;

    try {
        const payload = {
            node_id: currentLessonNode.id,
            title: currentLessonNode.title,
            type: currentLessonNode.type || 'subtopic'
        };

        console.log('[DEBUG] Enviando requisição para:', `${API_URL}/generate-lesson`);
        console.log('[DEBUG] Payload:', payload);

        const response = await fetch(`${API_URL}/generate-lesson`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        console.log('[DEBUG] Status da resposta:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('[DEBUG] Resultado:', result);

        if (result.status === 'success') {
            console.log('[DEBUG] Lição gerada com sucesso, recarregando...');
            
            // Recarrega a lição com o conteúdo gerado
            await showLesson(currentLessonNode);
            
            showToast('Conteúdo gerado com sucesso!', 'success');
        } else {
            throw new Error(result.message || 'Erro ao gerar conteúdo');
        }
    } catch (e) {
        console.error('[ERROR] Erro ao gerar conteúdo:', e);
        lessonContent.innerHTML = `
            <div style="text-align: center; padding: 60px 20px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">⚠️</div>
                <h2>Erro ao gerar conteúdo</h2>
                <p style="color: #f44336;">${e.message}</p>
                <p style="color: #888;">Verifique se o servidor está rodando e se a API key está configurada.</p>
                <button class="quiz-btn retry" onclick="generateLessonContent()" style="margin-top: 20px;">
                    🔄 Tentar Novamente
                </button>
            </div>
        `;
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

// Mantém função legada para compatibilidade (modo edição)
async function generateLessonForCurrentNode() {
    await generateLessonContent();
}

// --- CRUD E ROADMAPS ---

window.toggleEditMode = () => {
    isEditMode = !isEditMode;
    document.body.classList.toggle('edit-mode', isEditMode);
    editModeBtn.innerText = isEditMode ? "💾 Sair e Salvar" : "✏️ Modo Edição";
    if (!isEditMode) saveRoadmap();
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
    const modal = document.getElementById('modal-overlay');
    if (modal) {
        modal.style.display = 'flex';
        const firstInput = modal.querySelector('input, button');
        if (firstInput) setTimeout(() => firstInput.focus(), 100);
    }
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

async function generateQuizForCurrentLesson() {
    if (!currentLessonNode) {
        alert('Nenhuma lição selecionada.');
        return;
    }

    const btn = generateQuizBtn;
    const originalText = btn.innerText;
    btn.innerText = "🧠 Gerando quiz...";
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/quiz/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                node_id: currentLessonNode.id,
                title: currentLessonNode.title
            })
        });

        const result = await response.json();

        if (result.status === 'success') {
            currentQuizData = result.quiz;
            renderGeneratedQuiz(result.quiz);
        } else {
            throw new Error(result.message || 'Erro ao gerar quiz');
        }
    } catch (e) {
        console.error('Erro ao gerar quiz:', e);
        alert(`Erro ao gerar quiz: ${e.message}`);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

function renderGeneratedQuiz(questions) {
    quizContainer.innerHTML = '<h3>🧠 Quiz de Avaliação</h3>';
    quizContainer.style.display = 'block';

    const form = document.createElement('form');
    form.id = 'quiz-form';
    form.onsubmit = (e) => {
        e.preventDefault();
        submitQuizAnswers();
    };

    questions.forEach((q, idx) => {
        const qDiv = document.createElement('div');
        qDiv.className = 'quiz-question';
        
        const questionText = document.createElement('p');
        questionText.innerHTML = `<strong>${idx + 1}. ${q.question}</strong>`;
        qDiv.appendChild(questionText);

        q.options.forEach((opt, optIdx) => {
            const label = document.createElement('label');
            label.className = 'quiz-option-label';
            
            const radio = document.createElement('input');
            radio.type = 'radio';
            radio.name = `question-${idx}`;
            radio.value = optIdx;
            radio.required = true;
            
            label.appendChild(radio);
            label.appendChild(document.createTextNode(` ${opt}`));
            qDiv.appendChild(label);
        });

        form.appendChild(qDiv);
    });

    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'quiz-submit';
    submitBtn.innerText = 'Enviar Respostas';
    form.appendChild(submitBtn);

    quizContainer.appendChild(form);
}

async function submitQuizAnswers() {
    if (!currentQuizData || !currentLessonNode) return;

    const form = document.getElementById('quiz-form');
    const formData = new FormData(form);
    
    // Coleta respostas do usuário
    const userAnswers = {};
    currentQuizData.forEach((q, idx) => {
        const answer = formData.get(`question-${idx}`);
        if (answer !== null) {
            userAnswers[idx] = parseInt(answer);
        }
    });

    // Verifica se todas as perguntas foram respondidas
    if (Object.keys(userAnswers).length !== currentQuizData.length) {
        alert('Por favor, responda todas as perguntas.');
        return;
    }

    const submitBtn = form.querySelector('.quiz-submit');
    submitBtn.innerText = '⏳ Avaliando...';
    submitBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/quiz/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                node_id: currentLessonNode.id,
                title: currentLessonNode.title,
                quiz_data: currentQuizData,
                user_answers: userAnswers
            })
        });

        const result = await response.json();

        if (result.status === 'success') {
            displayQuizEvaluation(result.evaluation, userAnswers);
        } else {
            throw new Error(result.message || 'Erro ao avaliar quiz');
        }
    } catch (e) {
        console.error('Erro ao avaliar quiz:', e);
        alert(`Erro ao avaliar quiz: ${e.message}`);
        submitBtn.innerText = 'Enviar Respostas';
        submitBtn.disabled = false;
    }
}

function displayQuizEvaluation(evaluation, userAnswers) {
    quizContainer.innerHTML = '<h3>📊 Resultado da Avaliação</h3>';

    // Score e status
    const scoreDiv = document.createElement('div');
    scoreDiv.className = `quiz-score ${evaluation.passed ? 'passed' : 'failed'}`;
    scoreDiv.innerHTML = `
        <div class="score-value">${evaluation.score}%</div>
        <div class="score-status">${evaluation.passed ? '✅ Aprovado!' : '❌ Precisa revisar'}</div>
    `;
    quizContainer.appendChild(scoreDiv);

    // Feedback geral
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'quiz-feedback';
    feedbackDiv.innerHTML = `<p><strong>Feedback:</strong> ${evaluation.feedback}</p>`;
    quizContainer.appendChild(feedbackDiv);

    // Detalhes por questão
    if (evaluation.details && evaluation.details.length > 0) {
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'quiz-details';
        
        evaluation.details.forEach((detail) => {
            const detailItem = document.createElement('div');
            detailItem.className = `quiz-detail-item ${detail.correct ? 'correct' : 'incorrect'}`;
            
            const question = currentQuizData[detail.question_index];
            const userAnswerIdx = userAnswers[detail.question_index];
            
            detailItem.innerHTML = `
                <p><strong>Questão ${detail.question_index + 1}:</strong> ${question.question}</p>
                <p class="user-answer">Sua resposta: ${question.options[userAnswerIdx]}</p>
                <p class="correct-answer">Resposta correta: ${question.options[question.answer]}</p>
                <p class="detail-note">${detail.note}</p>
            `;
            
            detailsDiv.appendChild(detailItem);
        });
        
        quizContainer.appendChild(detailsDiv);
    }

    // Botões de ação
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'quiz-actions';
    
    const retryBtn = document.createElement('button');
    retryBtn.className = 'quiz-btn retry';
    retryBtn.innerText = '🔄 Tentar Novamente';
    retryBtn.onclick = () => generateQuizForCurrentLesson();
    
    const continueBtn = document.createElement('button');
    continueBtn.className = 'quiz-btn continue';
    continueBtn.innerText = evaluation.passed ? '✅ Marcar como Concluído' : '📖 Revisar Lição';
    continueBtn.onclick = () => {
        if (evaluation.passed) {
            completeNode(currentLessonNode.id);
            renderCompleteStatus();
        } else {
            // Rola para o topo da lição
            lessonContent.scrollIntoView({ behavior: 'smooth' });
        }
    };
    
    actionsDiv.appendChild(retryBtn);
    actionsDiv.appendChild(continueBtn);
    quizContainer.appendChild(actionsDiv);
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
    const progressBar = document.querySelector('.progress-container');
    if (progressBar) {
        progressBar.setAttribute('aria-valuenow', pct);
    }
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
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', data.title);

    // Header
    const header = document.createElement('div');
    header.className = 'review-modal-header';
    const h3 = document.createElement('h3');
    // P0: textContent em vez de innerHTML — previne XSS com dados do LLM
    h3.textContent = data.title;
    const closeBtn = document.createElement('button');
    closeBtn.className = 'review-modal-close';
    closeBtn.textContent = '×';
    closeBtn.setAttribute('aria-label', 'Fechar');
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
    lessonPanel.setAttribute('aria-hidden', 'true');
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
    
    window.flowchartInstance.init(currentRoadmap);
    
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
    window.flowchartInstance.init(currentRoadmap);
    
    // Re-aplicar nós completos
    setTimeout(() => {
        completedNodes.forEach(nodeId => {
            const nodeEl = document.getElementById(`node-${nodeId}`);
            if (nodeEl) nodeEl.classList.add('completed');
        });
    }, 100);
}

document.addEventListener('DOMContentLoaded', function() {
    init();
    initSearch();
    initFilters();

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modal-overlay');
            if (modal && modal.style.display !== 'none') {
                closeModal();
            }
            
            const panel = document.getElementById('lesson-panel');
            if (panel && panel.classList.contains('active')) {
                closePanel();
            }
            
            const filterPanel = document.getElementById('filter-panel');
            if (filterPanel && filterPanel.style.display !== 'none') {
                filterPanel.style.display = 'none';
            }
            return;
        }
        
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
    });

    document.getElementById('modal-overlay')?.addEventListener('keydown', function(e) {
        if (e.key !== 'Tab') return;
        
        const focusable = this.querySelectorAll('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
        }
    });

    // Mobile touch interactions (lessonPanel já declarado globalmente na linha 13)
    if (lessonPanel) {
        let touchStartX = 0;
        let touchCurrentX = 0;

        lessonPanel.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
            touchCurrentX = touchStartX;
        }, { passive: true });

        lessonPanel.addEventListener('touchmove', function(e) {
            touchCurrentX = e.touches[0].clientX;
        }, { passive: true });

        lessonPanel.addEventListener('touchend', function() {
            const diff = touchCurrentX - touchStartX;
            if (diff > 80 && isMobile()) {
                closePanel();
            }
        }, { passive: true });
    }
});

// P1: Removido setInterval(drawConnections, 5000) — causava layout thrashing periódico
// drawConnections é chamado apenas após eventos reais (resize, render)
window.addEventListener('resize', () => requestAnimationFrame(drawConnections));

window.loadRoadmap = loadRoadmap;
window.expandAllNodes = expandAllNodes;
window.collapseAllNodes = collapseAllNodes;
window.generateLessonForCurrentNode = generateLessonForCurrentNode;
window.generateLessonContent = generateLessonContent;
window.generateQuizForCurrentLesson = generateQuizForCurrentLesson;
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

// === SEARCH SYSTEM ===

let searchTimeout = null;
let searchResults = [];

function initSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            document.getElementById('search-results').style.display = 'none';
            return;
        }
        
        searchTimeout = setTimeout(() => performSearch(query), 300);
    });
    
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.blur();
            document.getElementById('search-results').style.display = 'none';
        }
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            navigateSearchResults(e.key === 'ArrowDown' ? 1 : -1);
        }
        if (e.key === 'Enter') {
            e.preventDefault();
            const highlighted = document.querySelector('.search-result-item.highlighted');
            if (highlighted) {
                highlighted.click();
            }
        }
    });
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-bar')) {
            document.getElementById('search-results').style.display = 'none';
        }
    });
}

function performSearch(query) {
    const q = query.toLowerCase();
    const allNodes = window.roadmapData ? flattenRoadmapData(window.roadmapData) : searchLoadedNodes();
    
    searchResults = allNodes.filter(node => 
        node.title.toLowerCase().includes(q)
    );
    
    renderSearchResults(searchResults, q);
}

function flattenRoadmapData(data) {
    const results = [];
    function walk(nodes, path) {
        if (!nodes) return;
        if (Array.isArray(nodes)) {
            nodes.forEach(n => walk(n, path));
        } else if (nodes.nodes) {
            nodes.nodes.forEach(n => walk(n, path));
        } else {
            results.push({
                title: nodes.title || nodes.name || '',
                difficulty: nodes.difficulty || '',
                id: nodes.id || '',
                path: path
            });
            if (nodes.subtopics) {
                nodes.subtopics.forEach(s => walk(s, [...path, nodes.title || nodes.name]));
            }
        }
    }
    walk(data, []);
    return results;
}

function searchLoadedNodes() {
    const nodes = document.querySelectorAll('.flowchart-node');
    return Array.from(nodes).map(n => ({
        title: n.querySelector('.flowchart-node-title')?.textContent || '',
        difficulty: n.classList.contains('difficulty-easy') ? 'easy' : 
                    n.classList.contains('difficulty-hard') ? 'hard' : 'medium',
        id: n.dataset.nodeId || '',
        path: []
    }));
}

function renderSearchResults(results, query) {
    const container = document.getElementById('search-results');
    if (!container) return;
    
    if (results.length === 0) {
        container.innerHTML = `<div class="search-no-results">Nenhum resultado para "${query}"</div>`;
        container.style.display = 'block';
        return;
    }
    
    let html = `<div class="search-result-count">${results.length} resultado${results.length !== 1 ? 's' : ''}</div>`;
    
    results.slice(0, 10).forEach((node, i) => {
        const diffClass = node.difficulty || 'medium';
        const pathStr = node.path.length > 0 ? node.path.join(' › ') : '';
        const highlightedTitle = node.title.replace(
            new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'),
            match => `<strong>${match}</strong>`
        );
        
        html += `
            <div class="search-result-item ${i === 0 ? 'highlighted' : ''}" 
                 data-id="${node.id}" 
                 role="option" 
                 aria-selected="false"
                 onclick="selectSearchResult('${node.id}')">
                <div>
                    <div class="result-title">${highlightedTitle}</div>
                    ${pathStr ? `<div class="result-path">${pathStr}</div>` : ''}
                </div>
                <span class="result-difficulty ${diffClass}">${diffClass}</span>
            </div>
        `;
    });
    
    container.innerHTML = html;
    container.style.display = 'block';
}

function navigateSearchResults(direction) {
    const items = document.querySelectorAll('.search-result-item');
    const currentIndex = Array.from(items).findIndex(el => el.classList.contains('highlighted'));
    const nextIndex = Math.max(0, Math.min(items.length - 1, currentIndex + direction));
    
    items.forEach(el => el.classList.remove('highlighted'));
    if (items[nextIndex]) {
        items[nextIndex].classList.add('highlighted');
        items[nextIndex].scrollIntoView({ block: 'nearest' });
    }
}

function selectSearchResult(nodeId) {
    document.getElementById('search-results').style.display = 'none';
    document.getElementById('search-input').value = '';
    
    const node = document.querySelector(`[data-node-id="${nodeId}"]`);
    if (node) {
        node.click();
        node.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// === FILTER SYSTEM ===

function toggleFilterPanel() {
    const panel = document.getElementById('filter-panel');
    if (!panel) return;
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

function initFilters() {
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            const filter = this.dataset.filter;
            const value = this.dataset.value;
            
            this.parentElement.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            applyFilters();
        });
    });
}

function applyFilters() {
    const difficulty = document.querySelector('.filter-chip.active[data-filter="difficulty"]')?.dataset.value || 'all';
    const status = document.querySelector('.filter-chip.active[data-filter="status"]')?.dataset.value || 'all';
    
    document.querySelectorAll('.flowchart-node').forEach(node => {
        let visible = true;
        
        if (difficulty !== 'all') {
            const nodeDiff = node.classList.contains('difficulty-easy') ? 'easy' :
                            node.classList.contains('difficulty-hard') ? 'hard' : 'medium';
            if (nodeDiff !== difficulty) visible = false;
        }
        
        if (status !== 'all') {
            const isCompleted = node.classList.contains('completed');
            if ((status === 'completed' && !isCompleted) || (status === 'pending' && isCompleted)) {
                visible = false;
            }
        }
        
        node.style.display = visible ? '' : 'none';
    });
    
    if (window.flowchartInstance && window.flowchartInstance.drawConnections) {
        window.flowchartInstance.drawConnections();
    }
}

function clearFilters() {
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.filter-chip[data-value="all"]').forEach(c => c.classList.add('active'));
    applyFilters();
    document.getElementById('filter-panel').style.display = 'none';
}

window.toggleFilterPanel = toggleFilterPanel;
window.clearFilters = clearFilters;
window.selectSearchResult = selectSearchResult;

// Toast Notification System
function showToast(message, type = 'success', duration = 3000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = { success: '✓', error: '✕', warning: '⚠' };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || '•'}</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function showLoadingSkeleton(container) {
    container.innerHTML = `
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text short"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text medium"></div>
        <div class="skeleton skeleton-card"></div>
    `;
}

function hideLoadingSkeleton(container) {
    container.querySelectorAll('.skeleton').forEach(el => el.remove());
}
