import roadmapData from './roadmap_data.js';

const nodesContainer = document.getElementById('roadmap-nodes');
const lessonPanel = document.getElementById('lesson-panel');
const lessonContent = document.getElementById('lesson-content');
const progressFill = document.getElementById('progress-fill');

let completedNodes = JSON.parse(localStorage.getItem('completedNodes') || '[]');

function renderRoadmap() {
    nodesContainer.innerHTML = '';
    const centralNodes = roadmapData.nodes.filter(n => n.type === 'central');
    
    centralNodes.forEach(centralNode => {
        // Cabeçalho da Seção (ex: Fundamentos de Programação)
        if (centralNode.group) {
            const sectionHeader = document.createElement('div');
            sectionHeader.className = 'section-title';
            sectionHeader.innerText = centralNode.group;
            nodesContainer.appendChild(sectionHeader);
        }

        const group = document.createElement('div');
        group.className = 'node-group';

        // Container para os Subtópicos (Esq/Dir)
        const childrenContainer = document.createElement('div');
        childrenContainer.className = 'node-children';
        
        // Coluna Esquerda
        const leftColumn = document.createElement('div');
        leftColumn.className = 'side-column left';
        
        // Coluna Direita
        const rightColumn = document.createElement('div');
        rightColumn.className = 'side-column right';

        // Nó Central
        const nodeEl = createNodeElement(centralNode);

        // Preenche as colunas baseado no 'side'
        const children = roadmapData.nodes.filter(n => centralNode.children.includes(n.id));
        children.forEach(child => {
            const childEl = createNodeElement(child);
            if (child.side === 'left') {
                leftColumn.appendChild(childEl);
            } else {
                rightColumn.appendChild(childEl);
            }
        });

        childrenContainer.appendChild(leftColumn);
        childrenContainer.appendChild(nodeEl); // Nó central no meio
        childrenContainer.appendChild(rightColumn);

        group.appendChild(childrenContainer);
        nodesContainer.appendChild(group);

        // Espaçador
        const spacer = document.createElement('div');
        spacer.style.height = '80px';
        nodesContainer.appendChild(spacer);
    });
    updateProgressBar();
}

function createNodeElement(node) {
    const el = document.createElement('div');
    el.className = `node ${node.type} ${completedNodes.includes(node.id) ? 'completed' : ''}`;
    el.id = `node-${node.id}`;
    el.innerText = node.title;
    el.onclick = () => showLesson(node);
    return el;
}

async function showLesson(node) {
    lessonContent.innerHTML = `<p style="color: #888;">Carregando lição de <strong>${node.title}</strong>...</p>`;
    lessonPanel.classList.add('active');

    try {
        const response = await fetch(`licoes/${node.id}.md`);
        if (!response.ok) throw new Error('Lição ainda não gerada.');
        
        const markdown = await response.text();
        const html = marked.parse(markdown);
        
        const isCompleted = completedNodes.includes(node.id);
        
        lessonContent.innerHTML = `
            ${html}
            <button class="complete-btn" onclick="window.toggleComplete('${node.id}')">
                ${isCompleted ? 'Marcar como não concluído' : 'Marcar como Concluído'}
            </button>
        `;
    } catch (error) {
        lessonContent.innerHTML = `
            <h2>${node.title}</h2>
            <p style="color: #ff4a4a;">⚠️ ${error.message}</p>
            <p>Execute o script <code>generate_lessons.py</code> para gerar o conteúdo desta lição.</p>
        `;
    }
}

window.toggleComplete = (nodeId) => {
    if (completedNodes.includes(nodeId)) {
        completedNodes = completedNodes.filter(id => id !== nodeId);
    } else {
        completedNodes.push(nodeId);
    }
    localStorage.setItem('completedNodes', JSON.stringify(completedNodes));
    renderRoadmap();
    
    const node = roadmapData.nodes.find(n => n.id === nodeId);
    if (node) showLesson(node);
};

function updateProgressBar() {
    const totalNodes = roadmapData.nodes.length;
    const completedCount = completedNodes.length;
    const percentage = (completedCount / totalNodes) * 100;
    progressFill.style.width = `${percentage}%`;
}

document.addEventListener('DOMContentLoaded', renderRoadmap);
