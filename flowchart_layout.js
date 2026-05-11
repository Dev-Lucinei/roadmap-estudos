/**
 * Sistema de Layout Flowchart/Mindmap
 * Renderiza roadmaps como fluxogramas conectados
 */

class FlowchartLayout {
    constructor(containerId, svgId) {
        this.container = document.getElementById(containerId);
        this.svg = document.getElementById(svgId);
        this.nodes = new Map();
        this.connections = [];
        this.expandedNodes = new Set();
        this.allNodes = new Map();
    }

    calculateLayout(roadmapData) {
        const positions = new Map();
        const centerX = this.container.offsetWidth / 2;
        const horizontalGap = 280;
        const minGap = 60;
        const startY = 150;
        const minTopMargin = 100; // Margem mínima do topo para evitar corte
        
        // FASE 1: Calcular altura necessária para cada nó central
        const nodeHeights = [];
        roadmapData.nodes.forEach((node) => {
            let totalHeight = 80;
            
            if (node.subtopics && node.subtopics.length > 0 && this.expandedNodes.has(node.id)) {
                let maxSubtopicHeight = 0;
                
                node.subtopics.forEach(subtopic => {
                    let subtopicHeight = 60; // Altura base do subtópico
                    
                    // Calcular altura dos sub-subtópicos se expandido
                    if (subtopic.subtopics && subtopic.subtopics.length > 0 && this.expandedNodes.has(subtopic.id)) {
                        // Altura = offset inicial (80) + (número de sub-subtópicos * gap (80))
                        subtopicHeight = 80 + (subtopic.subtopics.length * 80);
                    }
                    
                    maxSubtopicHeight += subtopicHeight + 20; // Gap entre subtópicos
                });
                
                totalHeight = Math.max(totalHeight, maxSubtopicHeight);
            }
            
            nodeHeights.push(totalHeight);
        });
        
        // FASE 2: Posicionar nós
        let currentY = startY;
        
        roadmapData.nodes.forEach((node, index) => {
            const nodeHeight = 80;
            const requiredHeight = nodeHeights[index];
            
            // Ajustar Y do nó central para garantir que subtópicos não sejam cortados
            let adjustedY = currentY;
            if (node.subtopics && node.subtopics.length > 0 && this.expandedNodes.has(node.id)) {
                const totalSubtopics = Math.max(
                    node.subtopics.filter((_, i) => i % 2 === 0).length,
                    node.subtopics.filter((_, i) => i % 2 !== 0).length
                );
                const subtopicStartY = currentY - ((totalSubtopics - 1) * 40);
                
                // Se subtópicos ficariam acima da margem mínima, ajustar
                if (subtopicStartY < minTopMargin) {
                    adjustedY = currentY + (minTopMargin - subtopicStartY);
                }
            }
            
            positions.set(node.id, {
                x: centerX,
                y: adjustedY,
                width: 280,
                height: nodeHeight,
                level: 0,
                node: node,
                hasSubtopics: node.subtopics && node.subtopics.length > 0
            });
            
            this.allNodes.set(node.id, node);

            if (node.subtopics && node.subtopics.length > 0 && this.expandedNodes.has(node.id)) {
                const leftSubtopics = [];
                const rightSubtopics = [];
                
                node.subtopics.forEach((subtopic, idx) => {
                    this.allNodes.set(subtopic.id, subtopic);
                    if (idx % 2 === 0) {
                        leftSubtopics.push(subtopic);
                    } else {
                        rightSubtopics.push(subtopic);
                    }
                });

                // Calcular altura total necessária para cada lado
                const calculateSideHeight = (subtopics) => {
                    let totalHeight = 0;
                    subtopics.forEach(sub => {
                        totalHeight += 60; // Altura do subtópico
                        if (sub.subtopics && sub.subtopics.length > 0 && this.expandedNodes.has(sub.id)) {
                            totalHeight += 20 + (sub.subtopics.length * 80); // Espaço para sub-subtópicos
                        }
                        totalHeight += 40; // Gap entre subtópicos
                    });
                    return totalHeight;
                };

                const leftHeight = calculateSideHeight(leftSubtopics);
                const rightHeight = calculateSideHeight(rightSubtopics);
                const maxHeight = Math.max(leftHeight, rightHeight);
                
                let subtopicStartY = adjustedY - (maxHeight / 2);
                
                // Garantir que subtópicos não fiquem acima da margem mínima
                if (subtopicStartY < minTopMargin) {
                    subtopicStartY = minTopMargin;
                }

                // Posicionar subtópicos da esquerda
                let currentLeftY = subtopicStartY;
                leftSubtopics.forEach((subtopic, idx) => {
                    const subY = currentLeftY;
                    positions.set(subtopic.id, {
                        x: centerX - horizontalGap,
                        y: subY,
                        width: 220,
                        height: 60,
                        level: 1,
                        node: subtopic,
                        parent: node.id,
                        hasSubtopics: subtopic.subtopics && subtopic.subtopics.length > 0
                    });

                    currentLeftY += 60; // Altura do subtópico

                    if (subtopic.subtopics && subtopic.subtopics.length > 0 && this.expandedNodes.has(subtopic.id)) {
                        currentLeftY += 20; // Gap antes dos sub-subtópicos
                        
                        subtopic.subtopics.forEach((subsubtopic, subIdx) => {
                            this.allNodes.set(subsubtopic.id, subsubtopic);
                            const subsubY = currentLeftY;
                            positions.set(subsubtopic.id, {
                                x: centerX - (horizontalGap * 2),
                                y: subsubY,
                                width: 180,
                                height: 50,
                                level: 2,
                                node: subsubtopic,
                                parent: subtopic.id,
                                hasSubtopics: false
                            });
                            
                            currentLeftY += 80; // Gap entre sub-subtópicos
                            
                            this.connections.push({
                                from: subtopic.id,
                                to: subsubtopic.id,
                                type: 'subtopic'
                            });
                        });
                    }

                    currentLeftY += 40; // Gap após o subtópico

                    this.connections.push({
                        from: node.id,
                        to: subtopic.id,
                        type: 'main'
                    });
                });

                // Posicionar subtópicos da direita
                let currentRightY = subtopicStartY;
                rightSubtopics.forEach((subtopic, idx) => {
                    const subY = currentRightY;
                    positions.set(subtopic.id, {
                        x: centerX + horizontalGap,
                        y: subY,
                        width: 220,
                        height: 60,
                        level: 1,
                        node: subtopic,
                        parent: node.id,
                        hasSubtopics: subtopic.subtopics && subtopic.subtopics.length > 0
                    });

                    currentRightY += 60; // Altura do subtópico

                    if (subtopic.subtopics && subtopic.subtopics.length > 0 && this.expandedNodes.has(subtopic.id)) {
                        currentRightY += 20; // Gap antes dos sub-subtópicos
                        
                        subtopic.subtopics.forEach((subsubtopic, subIdx) => {
                            this.allNodes.set(subsubtopic.id, subsubtopic);
                            const subsubY = currentRightY;
                            positions.set(subsubtopic.id, {
                                x: centerX + (horizontalGap * 2),
                                y: subsubY,
                                width: 180,
                                height: 50,
                                level: 2,
                                node: subsubtopic,
                                parent: subtopic.id,
                                hasSubtopics: false
                            });
                            
                            currentRightY += 80; // Gap entre sub-subtópicos
                            
                            this.connections.push({
                                from: subtopic.id,
                                to: subsubtopic.id,
                                type: 'subtopic'
                            });
                        });
                    }

                    currentRightY += 40; // Gap após o subtópico

                    this.connections.push({
                        from: node.id,
                        to: subtopic.id,
                        type: 'main'
                    });
                });
            }
            
            // Avançar Y baseado na altura real necessária
            // Usar metade da altura atual + metade da próxima para espaçamento equilibrado
            const nextIndex = index + 1;
            if (nextIndex < roadmapData.nodes.length) {
                const nextRequiredHeight = nodeHeights[nextIndex];
                const avgHeight = (requiredHeight + nextRequiredHeight) / 2;
                currentY += avgHeight + minGap;
            } else {
                currentY += requiredHeight + minGap;
            }
        });

        this.nodes = positions;
        return positions;
    }

    drawConnections() {
        this.svg.innerHTML = '';
        
        this.connections.forEach(conn => {
            const fromPos = this.nodes.get(conn.from);
            const toPos = this.nodes.get(conn.to);
            
            if (!fromPos || !toPos) return;

            const fromX = fromPos.x;
            const fromY = fromPos.y;
            const toX = toPos.x;
            const toY = toPos.y;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            
            const midX = (fromX + toX) / 2;
            const controlX = midX;
            const controlY = (fromY + toY) / 2;

            const d = `M ${fromX} ${fromY} Q ${controlX} ${controlY} ${toX} ${toY}`;
            
            path.setAttribute('d', d);
            path.setAttribute('stroke', conn.type === 'main' ? 'var(--accent-color)' : 'var(--glass-border)');
            path.setAttribute('stroke-width', conn.type === 'main' ? '2' : '1.5');
            path.setAttribute('fill', 'none');
            path.setAttribute('opacity', '0.6');
            path.setAttribute('stroke-dasharray', conn.type === 'main' ? '0' : '5,5');
            
            this.svg.appendChild(path);
        });
    }

    renderNodes() {
        this.container.innerHTML = '';
        
        this.nodes.forEach((pos, nodeId) => {
            const node = pos.node;
            const nodeEl = document.createElement('div');
            
            nodeEl.className = `flowchart-node level-${pos.level} difficulty-${node.difficulty || 'medium'}`;
            nodeEl.id = `node-${nodeId}`;
            nodeEl.style.left = `${pos.x - pos.width / 2}px`;
            nodeEl.style.top = `${pos.y - pos.height / 2}px`;
            nodeEl.style.width = `${pos.width}px`;
            nodeEl.style.minHeight = `${pos.height}px`;
            
            if (pos.hasSubtopics) {
                nodeEl.classList.add('has-subtopics');
                if (this.expandedNodes.has(nodeId)) {
                    nodeEl.classList.add('expanded');
                }
            }
            
            if (pos.hasSubtopics) {
                const expandIcon = document.createElement('span');
                expandIcon.className = 'flowchart-expand-icon';
                expandIcon.textContent = '▶';
                nodeEl.appendChild(expandIcon);
            }
            
            const title = document.createElement('div');
            title.className = 'flowchart-node-title';
            title.textContent = node.title;
            nodeEl.appendChild(title);
            
            if (node.difficulty) {
                const badge = document.createElement('span');
                badge.className = 'flowchart-node-badge';
                badge.textContent = node.difficulty;
                nodeEl.appendChild(badge);
            }
            
            nodeEl.onclick = (e) => {
                if (pos.hasSubtopics) {
                    e.stopPropagation();
                    this.toggleNode(nodeId);
                } else {
                    this.onNodeClick(node);
                }
            };
            
            nodeEl.ondblclick = (e) => {
                e.stopPropagation();
                this.onNodeClick(node);
            };
            
            this.container.appendChild(nodeEl);
        });
    }
    
    toggleNode(nodeId) {
        if (this.expandedNodes.has(nodeId)) {
            this.expandedNodes.delete(nodeId);
        } else {
            this.expandedNodes.add(nodeId);
        }
        
        this.render(this.currentRoadmap);
    }

    onNodeClick(node) {
        console.log('Node clicked:', node);
    }

    render(roadmapData) {
        console.log('FlowchartLayout.render: Iniciando', roadmapData);
        
        this.currentRoadmap = roadmapData;
        this.connections = [];
        
        console.log('FlowchartLayout.render: Calculando layout');
        this.calculateLayout(roadmapData);
        
        console.log('FlowchartLayout.render: Nós calculados:', this.nodes.size);
        
        const maxY = Math.max(...Array.from(this.nodes.values()).map(p => p.y + p.height));
        const minHeight = Math.max(maxY + 250, 800);
        this.svg.style.height = `${minHeight}px`;
        this.container.style.minHeight = `${minHeight}px`;
        
        console.log('FlowchartLayout.render: Altura SVG:', minHeight);
        
        console.log('FlowchartLayout.render: Desenhando conexões');
        this.drawConnections();
        
        console.log('FlowchartLayout.render: Renderizando nós');
        this.renderNodes();
        
        console.log('FlowchartLayout.render: Concluído');
    }
}

window.FlowchartLayout = FlowchartLayout;
