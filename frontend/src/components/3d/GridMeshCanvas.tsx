import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

// Static SVG Fallback for low power or reduced-motion
export const StaticGridFallback: React.FC = () => (
  <div className="w-full h-full min-h-[380px] bg-[#070A09] border border-[#263129] rounded-2xl flex items-center justify-center p-8 relative overflow-hidden">
    <svg className="absolute inset-0 w-full h-full opacity-30" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid-pattern" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#263129" strokeWidth="1" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid-pattern)" />
      <line x1="20%" y1="30%" x2="50%" y2="50%" stroke="#B6F542" strokeWidth="2" strokeDasharray="5,5" />
      <line x1="50%" y1="50%" x2="80%" y2="40%" stroke="#40D9E8" strokeWidth="2" />
      <line x1="50%" y1="50%" x2="65%" y2="75%" stroke="#F5B942" strokeWidth="2" />
      <circle cx="20%" cy="30%" r="8" fill="#B6F542" />
      <circle cx="50%" cy="50%" r="12" fill="#40D9E8" />
      <circle cx="80%" cy="40%" r="7" fill="#63D98A" />
      <circle cx="65%" cy="75%" r="9" fill="#FF6262" />
    </svg>
    <div className="relative z-10 text-center space-y-2">
      <span className="inline-block px-3 py-1 bg-[#161D19] border border-[#B6F542]/40 rounded-full text-xs font-semibold text-[#B6F542]">
        Synthetic Grid Demonstration Mesh
      </span>
      <p className="text-xs text-[#9BA8A0]">
        30 Feeders • 300 PMTs • 10,000 Connections Network Topology
      </p>
    </div>
  </div>
);

interface GridMeshCanvasProps {
  fallback?: boolean;
}

export const GridMeshCanvas: React.FC<GridMeshCanvasProps> = ({ fallback = false }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (fallback || prefersReducedMotion || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth || 500;
    const height = container.clientHeight || 380;

    // ─── Scene & Camera ─────────────────────────────────────────────────
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070a09, 0.035);
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 200);
    camera.position.set(0, 6, 18);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // ─── Color palette ──────────────────────────────────────────────────
    const COL_SUBSTATION = new THREE.Color('#B6F542');
    const COL_FEEDER     = new THREE.Color('#40D9E8');
    const COL_PMT        = new THREE.Color('#F5B942');
    const COL_CONSUMER   = new THREE.Color('#63D98A');
    const COL_ALERT      = new THREE.Color('#FF6262');
    const COL_EDGE       = new THREE.Color('#263129');
    const COL_FLOW       = new THREE.Color('#B6F542');

    // ─── Build topology: 1 substation → 6 feeders → ~18 PMTs → ~100 consumer clusters ──
    const masterGroup = new THREE.Group();
    scene.add(masterGroup);

    type NodeInfo = { pos: THREE.Vector3; tier: number; color: THREE.Color };
    const nodes: NodeInfo[] = [];
    const edges: { from: THREE.Vector3; to: THREE.Vector3 }[] = [];

    // Substation (center)
    const substationPos = new THREE.Vector3(0, 0, 0);
    nodes.push({ pos: substationPos, tier: 0, color: COL_SUBSTATION });

    const FEEDERS = 6;
    const PMTS_PER_FEEDER = 3;
    const CONSUMERS_PER_PMT = 6;

    for (let fi = 0; fi < FEEDERS; fi++) {
      const angle = (fi / FEEDERS) * Math.PI * 2 + Math.PI / 6;
      const radius = 5.5 + (Math.random() - 0.5) * 1.2;
      const feederPos = new THREE.Vector3(
        Math.cos(angle) * radius,
        (Math.random() - 0.5) * 1.5,
        Math.sin(angle) * radius
      );
      nodes.push({ pos: feederPos, tier: 1, color: COL_FEEDER });
      edges.push({ from: substationPos, to: feederPos });

      for (let pi = 0; pi < PMTS_PER_FEEDER; pi++) {
        const pmtAngle = angle + ((pi - 1) * 0.35) + (Math.random() - 0.5) * 0.15;
        const pmtRadius = radius + 3.0 + Math.random() * 1.5;
        const pmtPos = new THREE.Vector3(
          Math.cos(pmtAngle) * pmtRadius,
          (Math.random() - 0.5) * 2.0,
          Math.sin(pmtAngle) * pmtRadius
        );
        const isAlert = Math.random() < 0.15;
        nodes.push({ pos: pmtPos, tier: 2, color: isAlert ? COL_ALERT : COL_PMT });
        edges.push({ from: feederPos, to: pmtPos });

        for (let ci = 0; ci < CONSUMERS_PER_PMT; ci++) {
          const cAngle = pmtAngle + ((ci - CONSUMERS_PER_PMT / 2) * 0.12);
          const cRadius = pmtRadius + 1.8 + Math.random() * 1.2;
          const consumerPos = new THREE.Vector3(
            Math.cos(cAngle) * cRadius + (Math.random() - 0.5) * 0.6,
            (Math.random() - 0.5) * 2.5,
            Math.sin(cAngle) * cRadius + (Math.random() - 0.5) * 0.6
          );
          nodes.push({ pos: consumerPos, tier: 3, color: COL_CONSUMER });
          edges.push({ from: pmtPos, to: consumerPos });
        }
      }
    }

    // ─── Draw nodes as instanced spheres ────────────────────────────────
    const tierSizes = [0.45, 0.28, 0.18, 0.08];
    const tierSegments = [16, 12, 8, 4];

    for (let tier = 0; tier <= 3; tier++) {
      const tierNodes = nodes.filter(n => n.tier === tier);
      if (!tierNodes.length) continue;

      const geo = new THREE.SphereGeometry(tierSizes[tier], tierSegments[tier], tierSegments[tier]);
      const mat = new THREE.MeshBasicMaterial({ transparent: true, opacity: tier === 3 ? 0.6 : 0.9 });
      const mesh = new THREE.InstancedMesh(geo, mat, tierNodes.length);

      const dummy = new THREE.Object3D();
      const colorArr = new Float32Array(tierNodes.length * 3);

      tierNodes.forEach((n, i) => {
        dummy.position.copy(n.pos);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        colorArr[i * 3] = n.color.r;
        colorArr[i * 3 + 1] = n.color.g;
        colorArr[i * 3 + 2] = n.color.b;
      });

      mesh.instanceMatrix.needsUpdate = true;
      geo.setAttribute('color', new THREE.InstancedBufferAttribute(colorArr, 3));
      mat.vertexColors = false;
      // Per-instance color via onBeforeRender
      tierNodes.forEach((n, i) => {
        mesh.setColorAt(i, n.color);
      });
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
      masterGroup.add(mesh);
    }

    // ─── Glow rings around substations and feeders ──────────────────────
    const ringGeo = new THREE.RingGeometry(0.5, 0.7, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: COL_SUBSTATION, transparent: true, opacity: 0.25, side: THREE.DoubleSide
    });
    const substationRing = new THREE.Mesh(ringGeo, ringMat);
    substationRing.position.copy(substationPos);
    substationRing.rotation.x = -Math.PI / 2;
    masterGroup.add(substationRing);

    // ─── Draw edges (power lines) ───────────────────────────────────────
    const edgePositions: number[] = [];
    edges.forEach(e => {
      edgePositions.push(e.from.x, e.from.y, e.from.z, e.to.x, e.to.y, e.to.z);
    });
    const edgeGeo = new THREE.BufferGeometry();
    edgeGeo.setAttribute('position', new THREE.Float32BufferAttribute(edgePositions, 3));
    const edgeMat = new THREE.LineBasicMaterial({
      color: COL_EDGE, transparent: true, opacity: 0.35, linewidth: 1,
    });
    const edgeLines = new THREE.LineSegments(edgeGeo, edgeMat);
    masterGroup.add(edgeLines);

    // ─── Animated energy flow particles ─────────────────────────────────
    const FLOW_COUNT = 80;
    const flowGeo = new THREE.BufferGeometry();
    const flowPositions = new Float32Array(FLOW_COUNT * 3);
    const flowColors = new Float32Array(FLOW_COUNT * 3);
    const flowProgress = new Float32Array(FLOW_COUNT);
    const flowEdgeIdx = new Uint16Array(FLOW_COUNT);

    for (let i = 0; i < FLOW_COUNT; i++) {
      flowProgress[i] = Math.random();
      flowEdgeIdx[i] = Math.floor(Math.random() * edges.length);
      const edge = edges[flowEdgeIdx[i]];
      const t = flowProgress[i];
      flowPositions[i * 3] = edge.from.x + (edge.to.x - edge.from.x) * t;
      flowPositions[i * 3 + 1] = edge.from.y + (edge.to.y - edge.from.y) * t;
      flowPositions[i * 3 + 2] = edge.from.z + (edge.to.z - edge.from.z) * t;
      flowColors[i * 3] = COL_FLOW.r;
      flowColors[i * 3 + 1] = COL_FLOW.g;
      flowColors[i * 3 + 2] = COL_FLOW.b;
    }

    flowGeo.setAttribute('position', new THREE.BufferAttribute(flowPositions, 3));
    flowGeo.setAttribute('color', new THREE.BufferAttribute(flowColors, 3));
    const flowMat = new THREE.PointsMaterial({
      size: 0.12, vertexColors: true, transparent: true, opacity: 0.9,
      blending: THREE.AdditiveBlending, depthWrite: false,
    });
    const flowPoints = new THREE.Points(flowGeo, flowMat);
    masterGroup.add(flowPoints);

    // ─── Ground plane grid ──────────────────────────────────────────────
    const gridHelper = new THREE.GridHelper(30, 30, 0x1a241e, 0x111a14);
    gridHelper.position.y = -3.5;
    (gridHelper.material as THREE.Material).transparent = true;
    (gridHelper.material as THREE.Material).opacity = 0.3;
    masterGroup.add(gridHelper);

    // ─── Mouse parallax ─────────────────────────────────────────────────
    let mouseX = 0;
    let mouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      mouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    };

    container.addEventListener('mousemove', handleMouseMove);

    // ─── Animation loop ─────────────────────────────────────────────────
    let animationFrameId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      const dt = clock.getDelta();

      // Slow orbit + parallax
      masterGroup.rotation.y = elapsed * 0.05 + mouseX * 0.3;
      masterGroup.rotation.x = Math.sin(elapsed * 0.02) * 0.08 + mouseY * 0.15;

      // Substation glow pulse
      substationRing.scale.setScalar(1 + Math.sin(elapsed * 1.5) * 0.15);
      (substationRing.material as THREE.MeshBasicMaterial).opacity = 0.2 + Math.sin(elapsed * 1.5) * 0.1;

      // Animate flow particles along edges
      const posAttr = flowGeo.getAttribute('position') as THREE.BufferAttribute;
      for (let i = 0; i < FLOW_COUNT; i++) {
        flowProgress[i] += 0.004 + Math.random() * 0.002;
        if (flowProgress[i] > 1) {
          flowProgress[i] = 0;
          flowEdgeIdx[i] = Math.floor(Math.random() * edges.length);
        }
        const edge = edges[flowEdgeIdx[i]];
        const t = flowProgress[i];
        posAttr.setXYZ(
          i,
          edge.from.x + (edge.to.x - edge.from.x) * t,
          edge.from.y + (edge.to.y - edge.from.y) * t,
          edge.from.z + (edge.to.z - edge.from.z) * t
        );
      }
      posAttr.needsUpdate = true;

      renderer.render(scene, camera);
    };

    animate();

    // ─── Resize ─────────────────────────────────────────────────────────
    const handleResize = () => {
      if (!container) return;
      const newW = container.clientWidth;
      const newH = container.clientHeight;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      container.removeEventListener('mousemove', handleMouseMove);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [fallback, prefersReducedMotion]);

  if (fallback || prefersReducedMotion) {
    return <StaticGridFallback />;
  }

  return (
    <div
      ref={containerRef}
      className="w-full h-full min-h-[380px] bg-[#070A09]/90 border border-[#263129] rounded-2xl relative overflow-hidden shadow-2xl"
    >
      {/* Legend overlay */}
      <div className="absolute top-3 right-4 flex flex-col gap-1.5 text-[10px] font-mono-tech text-[#9BA8A0] bg-[#0C110E]/80 backdrop-blur-xs px-3 py-2 rounded-lg border border-[#263129] pointer-events-none">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-[#B6F542] inline-block" />
          <span>Substation (132 kV)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#40D9E8] inline-block" />
          <span>Feeders (11 kV)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-[#F5B942] inline-block" />
          <span>PMTs (Distribution)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-1 h-1 rounded-full bg-[#63D98A] inline-block" />
          <span>Consumer Clusters</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-[#FF6262] inline-block" />
          <span>High-Loss PMTs</span>
        </div>
      </div>

      <div className="absolute bottom-3 left-4 text-[11px] font-mono-tech text-[#9BA8A0] bg-[#0C110E]/80 backdrop-blur-xs px-3 py-1.5 rounded-md border border-[#263129] pointer-events-none flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-[#B6F542] animate-pulse inline-block" />
        Interactive 3D Grid Topology • 30 Feeders / 300 PMTs / 10k Connections
      </div>
    </div>
  );
};
