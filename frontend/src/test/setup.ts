import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Mock matchMedia for tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver for framer-motion useInView
class MockIntersectionObserver {
  readonly root: Element | null = null;
  readonly rootMargin: string = '';
  readonly thresholds: ReadonlyArray<number> = [];
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn(() => []);
}

Object.defineProperty(global, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: MockIntersectionObserver,
});
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: MockIntersectionObserver,
});

// Mock React Three Fiber Canvas & GridMeshCanvas for JSDOM
vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: any) => React.createElement('div', { 'data-testid': 'mock-canvas' }, children),
  useFrame: vi.fn(),
  useThree: () => ({ camera: {}, scene: {}, gl: {} }),
}));

vi.mock('../components/3d/GridMeshCanvas', () => ({
  GridMeshCanvas: () => React.createElement('div', { 'data-testid': 'grid-mesh-canvas' }, '3D Grid Topology Canvas Mock'),
  StaticGridFallback: () => React.createElement('div', null, 'Static Grid Fallback'),
}));

vi.mock('../components/3d/ElectricityShader', () => ({
  ElectricityShader: () => React.createElement('canvas', { 'data-testid': 'electricity-shader' }),
}));

// Mock echarts-for-react for JSDOM
vi.mock('echarts-for-react', () => ({
  default: () => React.createElement('div', { 'data-testid': 'mock-echart' }, 'EChart Mock Component'),
}));
