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

    // Scene & Camera setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.z = 10;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    container.appendChild(renderer.domElement);

    // Create 180 3D grid nodes
    const particleCount = 180;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const palette = [
      new THREE.Color('#B6F542'), // Lime Feeder
      new THREE.Color('#40D9E8'), // Cyan Smart Meter
      new THREE.Color('#F5B942'), // Amber Monthly
      new THREE.Color('#FF6262'), // Coral Priority
    ];

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.sin(i * 0.4) * 7) + (Math.random() - 0.5) * 2;
      positions[i * 3 + 1] = (Math.cos(i * 0.3) * 4) + (Math.random() - 0.5) * 2;
      positions[i * 3 + 2] = (Math.sin(i * 0.5) * 3) + (Math.random() - 0.5) * 2;

      const col = palette[i % palette.length];
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.28,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    // Mouse Parallax & Animation Loop
    let mouseX = 0;
    let mouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      mouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    };

    container.addEventListener('mousemove', handleMouseMove);

    let animationFrameId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      points.rotation.y = elapsedTime * 0.08 + mouseX * 0.2;
      points.rotation.x = elapsedTime * 0.04 + mouseY * 0.1;

      renderer.render(scene, camera);
    };

    animate();

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
      geometry.dispose();
      material.dispose();
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
      <div className="absolute bottom-3 left-4 text-[11px] font-mono-tech text-[#9BA8A0] bg-[#0C110E]/80 backdrop-blur-xs px-3 py-1 rounded-md border border-[#263129] pointer-events-none">
        Interactive 3D Grid Topology • 30 Feeders / 300 PMTs / 10k Connections
      </div>
    </div>
  );
};
