import roadmapData from './roadmap_data.js';

const nodesContainer = document.getElementById('roadmap-nodes');
const lessonPanel = document.getElementById('lesson-panel');
const lessonContent = document.getElementById('lesson-content');
const progressFill = document.getElementById('progress-fill');
const svg = document.getElementById('roadmap-svg');
const view = document.getElementById('roadmap-view');

let completedNodes = JSON.parse(localStorage.getItem('completedNodes') || '[]');

function renderRoadmap() {
    nodesContainer.innerHTML = '';
    const centralNodes = roadmapData.nodes.filter(n => n.type === 'central');
    
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
        
        const leftColumn = document.createElement('div');
        leftColumn.className = 'side-column left';
        const rightColumn = document.createElement('div');
        rightColumn.className = 'side-column right';

        const nodeEl = createNodeElement(centralNode);

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
        childrenContainer.appendChild(nodeEl);
        childrenContainer.appendChild(rightColumn);

        group.appendChild(childrenContainer);
        nodesContainer.appendChild(group);

        const spacer = document.createElement('div');
        spacer.style.height = '120px';
        nodesContainer.appendChild(spacer);
    });
    updateProgressBar();
    // Aguarda um pouco para o layout estabilizar antes de desenhar
    requestAnimationFrame(() => setTimeout(drawConnections, 300));
}

function createNodeElement(node) {
    const el = document.createElement('div');
    el.className = `node ${node.type} ${completedNodes.includes(node.id) ? 'completed' : ''}`;
    el.id = `node-${node.id}`;
    el.innerText = node.title;
    el.onclick = () => showLesson(node);
    return el;
}

// Função para pegar a posição real de um elemento relativa ao container do Roadmap
function getAbsoluteCoords(el) {
    let top = 0, left = 0;
    let currentEl = el;
    while (currentEl && currentEl !== view) {
        top += currentEl.offsetTop || 0;
        left += currentEl.offsetLeft || 0;
        currentEl = currentEl.offsetParent;
    }
    return {
        x: left + el.offsetWidth / 2,
        y: top + el.offsetHeight / 2
    };
}

function drawConnections() {
    svg.innerHTML = '';
    const fullHeight = view.scrollHeight;
    const fullWidth = view.scrollWidth;
    svg.setAttribute('height', fullHeight);
    svg.setAttribute('width', fullWidth);

    const centralNodes = roadmapData.nodes.filter(n => n.type === 'central');
    
    centralNodes.forEach((centralNode, index) => {
        const parentEl = document.getElementById(`node-${centralNode.id}`);
        if (!parentEl) return;

        const pCoords = getAbsoluteCoords(parentEl);

        // 1. Conectar Filhos
        centralNode.children.forEach(childId => {
            const childEl = document.getElementById(`node-${childId}`);
            if (!childEl) return;

            const cCoords = getAbsoluteCoords(childEl);
            drawBezier(pCoords.x, pCoords.y, cCoords.x, cCoords.y);
        });

        // 2. Conectar Espinha Dorsal (Pai atual -> Próximo Pai)
        if (index < centralNodes.length - 1) {
            const nextNode = centralNodes[index + 1];
            const nextEl = document.getElementById(`node-${nextNode.id}`);
            if (nextEl) {
                const nCoords = getAbsoluteCoords(nextEl);
                drawLine(pCoords.x, pCoords.y, nCoords.x, nCoords.y, true);
            }
        }
    });
}

function drawBezier(x1, y1, x2, y2) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const controlY = y1 + (y2 - y1) / 2;
    const d = `M ${x1} ${y1} C ${x1} ${controlY}, ${x2} ${controlY}, ${x2} ${y2}`;
    path.setAttribute('d', d);
    path.setAttribute('class', 'roadmap-path');
    svg.appendChild(path);
}

function drawLine(x1, y1, x2, y2, isSpine = false) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M ${x1} ${y1} L ${x2} ${y2}`);
    path.setAttribute('class', `roadmap-path ${isSpine ? 'spine-line' : ''}`);
    svg.appendChild(path);
}

async function showLesson(node) {
    lessonContent.innerHTML = `<p style="color: #888;">Carregando lição de <strong>${node.title}</strong>...</p>`;
    lessonPanel.classList.add('active');

    try {
        const response = await fetch(`licoes/${node.id}.md`);
        if (!response.ok) throw new Error('Lição ainda não gerada.');
        const markdown = await response.text();
        lessonContent.innerHTML = marked.parse(markdown);
    } catch (error) {
        lessonContent.innerHTML = `<h2>${node.title}</h2><p style="color: #ff4a4a;">⚠️ ${error.message}</p>`;
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
    const percentage = Math.round((completedCount / totalNodes) * 100);
    progressFill.style.width = `${percentage}%`;
    document.getElementById('progress-percent').innerText = `${percentage}%`;
}

window.goToNext = (nodeId) => {
    const node = roadmapData.nodes.find(n => n.id === nodeId);
    if (node) {
        const el = document.getElementById(`node-${nodeId}`);
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        showLesson(node);
    }
};

// Inicialização
document.addEventListener('DOMContentLoaded', renderRoadmap);

window.addEventListener('resize', () => {
    requestAnimationFrame(drawConnections);
});

// Redesenha periodicamente para garantir alinhamento em zooms e mudanças lentas
setInterval(drawConnections, 2000);

// Observador de mudança de tamanho para manter sincronizado
const resizeObserver = new ResizeObserver(() => {
    drawConnections();
});
resizeObserver.observe(nodesContainer);

window.closePanel = () => {
    lessonPanel.classList.remove('active');
};
