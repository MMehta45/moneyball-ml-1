import React, { useCallback, useLayoutEffect, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  ConnectionMode,
  Controls,
  Position,
  Handle,
  MarkerType,
  Background,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import data from '../../data_updated2.json';

const nodeWidth = 140;
const nodeHeight = 140;
const columnSpacing = 240;
const rowSpacing = 180;

const formatCourseCode = (courseCode: string) => courseCode.replace(/([A-Z]+)(\d+)/, '$1 $2');
const stripTag = (courseCode: string) => courseCode.replace(/_(U|C)$/, '');
const getLocationLabel = (courseCode: string) => (courseCode.endsWith('_C') ? 'Collin' : 'Campus');

// Helper to determine difficulty color
const getDifficultyColor = (score: number): string => {
  if (score < 0.75) return '#189245'; // Green for easy
  if (score > 0.85) return '#cb3b3b'; // Yellow for medium
  return '#d4a20a'; // Red for hard
};

// Custom node with handles on left/right sides
const CourseNode: React.FC<{ data: any }> = ({ data }) => {
  return (
    <div
      onMouseEnter={() => data.onHover?.(data.id)}
      onClick={() => data.onUnhover?.()}
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Space Mono, monospace',
        fontSize: '19px',
        fontWeight: 'bold',
        cursor: 'pointer',
        
      }}
    >
      <Handle type="target" position={Position.Left} />
      <div>{data.label}</div>
      <div style={{ fontSize: '14px', marginTop: '4px', color: '#f8fafc', fontWeight: 'bold', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        Difficulty: {data.difficulty?.toFixed(2)}
      </div>
      <div style={{ fontSize: '13px', marginTop: '4px', color: '#f8fafc', fontWeight: 'bold', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        {data.location}
      </div>
      <Handle type="source" position={Position.Right} />
      
    </div>
  );
};

interface GraphFrontendProps {
  scheduleVersion: number
  darkMode: boolean
  onDarkModeToggle: () => void
  onReset: () => void
}

const GraphFrontend: React.FC<GraphFrontendProps> = ({ scheduleVersion }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [scheduleData, setScheduleData] = useState<any[]>([]);
  const originalNodesRef = React.useRef<Node[] | null>(null);
  const originalEdgesRef = React.useRef<Edge[] | null>(null);

  // Find all connected nodes (prerequisites and dependents)
  const findConnectedNodes = (nodeId: string, edgesList: Edge[]): Set<string> => {
  const connected = new Set<string>();
  connected.add(nodeId);

  edgesList.forEach((edge) => {
    if (edge.target === nodeId) connected.add(edge.source); // direct prereqs
    if (edge.source === nodeId) connected.add(edge.target); // direct dependents
  });

  return connected;
};

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const restoreOriginalLayout = () => {
    if (originalNodesRef.current) {
      setNodes(originalNodesRef.current);
    }
    if (originalEdgesRef.current) {
      setEdges(originalEdgesRef.current);
    }
  };

  // memoize nodeTypes so ReactFlow doesn't warn about new objects each render
  const nodeTypes = React.useMemo(() => ({ courseNode: CourseNode }), []);

  React.useEffect(() => {
    let cancelled = false;

    const loadSchedule = async () => {
      const response = await fetch(`/schedule.json?v=${scheduleVersion}`, { cache: 'no-store' });
      const nextSchedule = await response.json();
      if (!cancelled) {
        setScheduleData(nextSchedule);
      }
    };

    void loadSchedule();

    return () => {
      cancelled = true;
    };
  }, [scheduleVersion]);

  useLayoutEffect(() => {
    if (scheduleData.length === 0) {
      return;
    }

    // Get all courses from data
    const courseData = data as Record<string, any>;

    // Collect all unique courses from schedule
    const scheduleCourses = new Set<string>();
    scheduleData.forEach(sem => {
      sem.courses.forEach((course: string) => scheduleCourses.add(stripTag(course)));
    });

    const semesterOrder = scheduleData
      .slice()
      .sort((a, b) => a.semester - b.semester)
      .map((sem) => sem.semester);

    const semesterCourseMap: Record<number, string[]> = {};
    semesterOrder.forEach((semester) => {
      semesterCourseMap[semester] = scheduleData
        .find((sem) => sem.semester === semester)
        ?.courses || [];
    });

    const initialNodes: Node[] = [];
    const initialEdges: Edge[] = [];
    const edgeSet = new Set<string>(); // Prevent duplicate edges

 

    // Add semester headers
    semesterOrder.forEach((semester) => {
      const semesterData = scheduleData.find(sem => sem.semester === semester);
      const headerLabel = `Semester ${semester}\n${semesterData?.term || ''}`;
      initialNodes.push({
        id: `semester-${semester}`,
        data: { label: headerLabel },
        position: {
          x: (semester - 1) * columnSpacing,
          y: -150,
        },
        draggable: false,
        selectable: false,
        style: {
          width: nodeWidth + 10,
          height: 85,
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: 8,
          backgroundColor: '#183f27',
          color: '#e5e7eb',
          border: '0px solid #4f46e5',
          fontSize: '18px',
          fontWeight: 'bold',
          fontFamily: 'Space Mono, monospace',
          whiteSpace: 'pre-line',
        },
      });
    });

    semesterOrder.forEach((semester) => {
      const courses = semesterCourseMap[semester] || [];
      courses.forEach((rawCourseCode, index) => {
        const courseCode = stripTag(rawCourseCode);
        if (courseData[courseCode]) {
          const displayCode = formatCourseCode(courseCode);
          const difficultyScore = courseData[courseCode].difficulty_Score || 0;
          const backgroundColor = getDifficultyColor(difficultyScore);
          initialNodes.push({
            id: courseCode,
            type: 'courseNode',
            data: {
              label: displayCode,
              location: getLocationLabel(rawCourseCode),
              difficulty: difficultyScore,
              id: courseCode,
              onHover: (nodeId: string) => {
                // compute connected set using the current edge snapshot (initialEdges captured in layout)
                const connected = findConnectedNodes(nodeId, initialEdges);
                // original snapshots are captured when the layout is first created

                setNodes((nds) =>
                  nds.map((n) => ({
                    ...n,
                    data: { ...n.data, isInPath: connected.has(n.id) },
                    style: {
                      ...n.style,
                      opacity: connected.has(n.id) ? 1 : 0.15,
                      transition: 'opacity 0.2s ease',
                    },
                  }))
                );

                setEdges((eds) =>
                  eds.map((e) => {
                    const isConnected = connected.has(e.source) && connected.has(e.target);
                    return {
                      ...e,
                      style: {
                        ...e.style,
                        stroke: isConnected ? '#e9690e' : 'transparent',
                        strokeWidth: isConnected ? 2 : 0,
                        transition: 'opacity 0.2s ease',
                      },
                      markerEnd: {
                        type: MarkerType.ArrowClosed,
                        color: isConnected ? '#e9690e' : 'transparent',
                      },
                      animated: isConnected,
                    };
                  })
                );
              },
              onUnhover: () => {
                // restore original snapshots if available, otherwise reset to visible
                if (originalNodesRef.current) {
                  setNodes(originalNodesRef.current);
                  originalNodesRef.current = null;
                } else {
                  setNodes((nds) =>
                    nds.map((n) => ({
                      ...n,
                      data: { ...n.data, isInPath: true },
                      style: { ...n.style, opacity: 1, transition: 'opacity 0.2s ease' },
                    }))
                  );
                }

                if (originalEdgesRef.current) {
                  setEdges(originalEdgesRef.current);
                  originalEdgesRef.current = null;
                } else {
                  setEdges((eds) =>
                    eds.map((e) => ({
                      ...e,
                      style: { ...e.style, stroke: '#e9690e', strokeWidth: 2, transition: 'opacity 0.2s ease' },
                      markerEnd: { type: MarkerType.ArrowClosed, color: '#e9690e' },
                      animated: true,
                    }))
                  );
                }
              },
            },
            position: {
              x: (semester - 1) * columnSpacing,
              y: index * rowSpacing,
            },
            style: {
              width: nodeWidth,
              height: nodeHeight,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              padding: 8,
              backgroundColor: backgroundColor,
              color: '#f8fafc',
              border: '2px solid rgba(255, 255, 255, 0.4)',
              boxShadow: '0 10px 20px rgba(0, 0, 0, 0.2)',
            },
          });

          const prereqs = courseData[courseCode].prereqs || [];
          prereqs.forEach((prereq: string) => {
            if (prereq && prereq !== '') {
              const altPrereqs = prereq.split('/').map((p: string) => p.trim());
              altPrereqs.forEach((alt) => {
                if (alt && scheduleCourses.has(alt)) {
                  const edgeId = `${alt}-${courseCode}`;
                  if (!edgeSet.has(edgeId)) {
                    edgeSet.add(edgeId);
                    initialEdges.push({
                      id: edgeId,
                      source: alt,
                      target: courseCode,
                      markerEnd: {
                        type: MarkerType.ArrowClosed,
                        color: '#e9690e',
                      },
                      animated: true,
                      style: {
                        stroke: '#e9690e',
                        strokeWidth: 2,
                      },
                    });
                  }
                }
              });
            }
          });
        }
      });
    });

    setNodes(initialNodes);
    setEdges(initialEdges);

    // capture the original layout snapshots so hover/unhover can reliably restore
    originalNodesRef.current = initialNodes.slice();
    originalEdgesRef.current = initialEdges.slice();
  }, [scheduleData, setNodes, setEdges]);

  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative', paddingTop: '23px', boxSizing: 'border-box' }}>
      <button
        onClick={() => setDarkMode((prev) => !prev)}
        style={{
          position: 'absolute',
          top: 16,
          right: 16,
          zIndex: 10,
          padding: '8px 16px',
          borderRadius: '8px',
          border: 'none',
          cursor: 'pointer',
          backgroundColor: darkMode ? '#e9690e' : '#183f27',
          color: darkMode ? '#1f2937' : '#e5e7eb',
          fontFamily: 'Space Mono, monospace',
          fontWeight: 'bold',
        }}
      >
        {darkMode ? '☀️ Light' : '🌙 Dark'}
      </button>
      <div style={{
        position: 'absolute',
        top: 16,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 10,
        color: darkMode ? '#e9690e' : '#e9690e',
        fontFamily: 'Space Mono, monospace',
        fontSize: '40px',
        fontWeight: 'bold',
        pointerEvents: 'none',
      }}>
        Your Four Year Plan
      </div>
      <div style={{
        position: 'absolute',
        bottom: 24,
        right: 24,
        zIndex: 10,
        backgroundColor: darkMode ? 'rgba(31, 41, 55, 0.9)' : 'rgba(229, 231, 235, 0.9)',
        border: `1px solid ${darkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)'}`,
        borderRadius: '8px',
        padding: '16px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        fontSize: '12px',
        color: darkMode ? '#e5e7eb' : '#1f2937',
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Difficulty</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <div style={{
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            backgroundColor: '#189245',
          }} />
          <span>Easy (&lt; 0.75)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <div style={{
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            backgroundColor: '#d4a20a',
          }} />
          <span>Average (0.75 - 0.85)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            backgroundColor: '#cb3b3b',
          }} />
          <span>Hard (&gt; 0.85)</span>
        </div>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={() => restoreOriginalLayout()}
        connectionMode={ConnectionMode.Loose}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <Background variant={BackgroundVariant.Lines} gap={50} color={darkMode ? "rgba(255,255,255,0.1)" : "rgba(64,64,64,0.1)"} />
      </ReactFlow>
    </div>
  );
};

export default GraphFrontend;
