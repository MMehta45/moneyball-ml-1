import React, { useCallback, useLayoutEffect, useState, useEffect } from 'react';
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
} from 'reactflow';
import 'reactflow/dist/style.css';
import data from '../data_updated2.json';
import schedule from '../mock_schedule.json';

const nodeWidth = 140;
const nodeHeight = 140;
const columnSpacing = 240;
const rowSpacing = 180;

const formatCourseCode = (courseCode: string) => courseCode.replace(/([A-Z]+)(\d+)/, '$1 $2');

// Helper to determine difficulty color
const getDifficultyColor = (score: number): string => {
  if (score < 0.75) return '#22c55e'; // Green for easy
  if (score > 0.85) return '#ef4444'; // Yellow for medium
  return '#eab308'; // Red for hard
};

// Custom node with handles on left/right sides
const CourseNode: React.FC<{ data: any }> = ({ data }) => {
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        fontSize: '18px',
        fontWeight: 'bold',
      }}
    >
      <Handle type="target" position={Position.Left} />
      <div>{data.label}</div>
      <div style={{ fontSize: '15px', marginTop: '4px', color: '#f8fafc', fontWeight: 'bold' }}>
        Difficulty: {data.difficulty?.toFixed(2)}
      </div>
      <div style={{ fontSize: '13px', marginTop: '4px', color: '#f8fafc', fontWeight: 'bold' }}>
        Campus
      </div>
      <Handle type="source" position={Position.Right} />
      
    </div>
  );
};

const GraphFrontend: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [darkMode, setDarkMode] = useState<boolean>(false);

  useEffect(() => {
    document.body.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  useLayoutEffect(() => {
    // Get all courses from data
    const courseData = data as Record<string, any>;
    const scheduleData = schedule as any[];

    // Collect all unique courses from schedule
    const scheduleCourses = new Set<string>();
    scheduleData.forEach(sem => {
      sem.courses.forEach((course: string) => scheduleCourses.add(course));
    });

    const semesterOrder = scheduleData
      .slice()
      .sort((a, b) => a.semester - b.semester)
      .map((sem) => sem.semester);

    const semesterCourseMap: Record<number, string[]> = {};
    semesterOrder.forEach((semester) => {
      semesterCourseMap[semester] = scheduleData
        .find((sem) => sem.semester === semester)
        ?.courses.filter((course: string) => scheduleCourses.has(course)) || [];
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
          width: nodeWidth,
          height: 80,
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: 8,
          backgroundColor: '#1f2937',
          color: '#e5e7eb',
          border: '2px solid #4f46e5',
          fontSize: '16px',
          fontWeight: 'bold',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          whiteSpace: 'pre-line',
        },
      });
    });

    semesterOrder.forEach((semester) => {
      const courses = semesterCourseMap[semester] || [];
      courses.forEach((courseCode, index) => {
        if (courseData[courseCode]) {
          const displayCode = formatCourseCode(courseCode);
          const difficultyScore = courseData[courseCode].difficulty_Score || 0;
          const backgroundColor = getDifficultyColor(difficultyScore);
          initialNodes.push({
            id: courseCode,
            type: 'courseNode',
            data: { label: displayCode, difficulty: difficultyScore },
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
                        color: '#13d0f1',
                      },
                      animated: true,
                      style: {
                        stroke: '#13d0f1',
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
  }, [setNodes, setEdges]);

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
          backgroundColor: darkMode ? '#e5e7eb' : '#1f2937',
          color: darkMode ? '#1f2937' : '#e5e7eb',
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
        color: darkMode ? '#ffffff' : '#1f2937',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        fontSize: '30px',
        fontWeight: 'bold',
        pointerEvents: 'none',
      }}>
        Your Four Year Plan
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        connectionMode={ConnectionMode.Loose}
        nodeTypes={{ courseNode: CourseNode }}
        fitView
      >
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default GraphFrontend;