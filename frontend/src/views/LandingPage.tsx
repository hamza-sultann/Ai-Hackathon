import React, { useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import { Zap, ShieldCheck, ArrowRight, Activity, Lock, ChevronDown, Search, ClipboardList, Lightbulb, Scale } from 'lucide-react';
import { ElectricityShader } from '../components/3d/ElectricityShader';
import { RESPONSIBLE_TERMINOLOGY } from '../config/tokens';
import { ROUTES } from '../config/routes';

/* ─── Scroll-triggered section wrapper ─── */
const ScrollReveal: React.FC<{
  children: React.ReactNode;
  className?: string;
  delay?: number;
}> = ({ children, className = '', delay = 0 }) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 60 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 60 }}
      transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
};

/* ─── Staggered child container ─── */
const StaggerContainer: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-60px' });

  return (
    <motion.div
      ref={ref}
      className={className}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.12 } },
      }}
    >
      {children}
    </motion.div>
  );
};

const staggerChild = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const } },
};

/* ─── Counter animation hook ─── */
const AnimatedCounter: React.FC<{ value: string; color: string; label: string }> = ({
  value,
  color,
  label,
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });

  return (
    <div ref={ref} className="text-center">
      <motion.div
        className="font-mono-tech text-2xl font-extrabold"
        style={{ color }}
        initial={{ opacity: 0, scale: 0.5 }}
        animate={isInView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 0.5, type: 'spring', stiffness: 200 }}
      >
        {value}
      </motion.div>
      <div className="text-[11px] uppercase tracking-[0.05em] font-bold text-[#9BA8A0] mt-1">
        {label}
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════════
   LANDING PAGE
   ═══════════════════════════════════════════════════════════════ */
export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });
  // Parallax values
  const shaderY = useTransform(scrollYProgress, [0, 1], ['0%', '30%']);
  const shaderOpacity = useTransform(scrollYProgress, [0, 0.7], [0.45, 0]);
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '20%']);

  const steps = [
    {
      icon: <Scale className="w-6 h-6" />,
      num: '01',
      title: 'Measure Grid Balance',
      desc: 'Calculate physical energy flows against recorded consumption at edge nodes.',
    },
    {
      icon: <Search className="w-6 h-6" />,
      num: '02',
      title: 'Detect Anomalies',
      desc: 'Identify statistical deviations in usage patterns comparing historical baselines.',
    },
    {
      icon: <Lightbulb className="w-6 h-6" />,
      num: '03',
      title: 'Explain Evidence',
      desc: 'Generate human-readable rationale linking physical models to predicted losses.',
    },
    {
      icon: <ClipboardList className="w-6 h-6" />,
      num: '04',
      title: 'Prioritize Inspections',
      desc: 'Rank targets by confidence and revenue impact to direct field crews effectively.',
    },
  ];

  const capabilities = [
    {
      code: 'SYS-01',
      title: 'Grid Loss Monitoring',
      desc: 'Continuous tracking of technical vs. commercial losses across transformer hierarchies.',
      color: '#B6F542',
    },
    {
      code: 'INV-02',
      title: 'Consumer Investigation',
      desc: 'Deep dive into individual meter profiles, comparing declared load vs actual draw.',
      color: '#40D9E8',
    },
    {
      code: 'TMP-03',
      title: 'Monthly vs. Hourly Analysis',
      desc: 'Reconcile disparate data frequencies to form a cohesive view of grid health over time.',
      color: '#F5B942',
    },
    {
      code: 'OP-04',
      title: 'Inspection Job-Cards',
      desc: 'Generate structured field tasks with precise coordinates and expected anomaly types.',
      color: '#63D98A',
    },
  ];

  return (
    <div className="min-h-screen bg-[#070A09] text-[#F3F7F4] font-sans selection:bg-[#B6F542] selection:text-[#070A09] overflow-x-hidden">
      {/* ── Top Navigation ── */}
      <header className="fixed top-0 left-0 w-full z-50 bg-[#070A09]/80 backdrop-blur-md border-b border-[#263129]/60 h-16 flex justify-between items-center px-6 transition-colors">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-[#B6F542]" />
          <span className="font-heading font-semibold text-xl tracking-tight text-[#F3F7F4]">
            Istikshaf
          </span>
        </div>
        <nav className="hidden md:flex items-center gap-8">
          <a href="#how-it-works" className="text-sm text-[#9BA8A0] hover:text-[#F3F7F4] transition-colors">
            How It Works
          </a>
          <a href="#capabilities" className="text-sm text-[#9BA8A0] hover:text-[#F3F7F4] transition-colors">
            Capabilities
          </a>
          <a href="#responsible-use" className="text-sm text-[#9BA8A0] hover:text-[#F3F7F4] transition-colors">
            Responsible Use
          </a>
        </nav>
        <Link
          to={ROUTES.WORKSPACES}
          className="hidden md:flex items-center justify-center bg-[#B6F542] text-[#11150a] px-5 py-2 rounded-md text-sm font-semibold hover:bg-[#CAFF69] transition-colors"
        >
          Launch Dashboard
        </Link>
      </header>

      {/* ══════════════════════════════════════════════════
          HERO SECTION — fullscreen shader background
         ══════════════════════════════════════════════════ */}
      <section
        ref={heroRef}
        className="relative min-h-screen flex flex-col justify-center items-center text-center px-6 pt-16 overflow-hidden"
      >
        {/* Shader background — fullscreen behind hero, parallax fades on scroll */}
        <motion.div
          className="absolute inset-0 w-full h-full z-0 pointer-events-none"
          style={{ y: shaderY, opacity: shaderOpacity }}
        >
          <ElectricityShader className="absolute inset-0 w-full h-full" />
        </motion.div>

        {/* Subtle grid overlay */}
        <div
          className="absolute inset-0 z-[1] pointer-events-none opacity-[0.04]"
          style={{
            backgroundSize: '40px 40px',
            backgroundImage:
              'linear-gradient(to right, rgba(140,148,124,0.3) 1px, transparent 1px), linear-gradient(to bottom, rgba(140,148,124,0.3) 1px, transparent 1px)',
          }}
        />

        {/* Hero Content */}
        <motion.div
          className="relative z-10 max-w-4xl mx-auto flex flex-col items-center gap-6"
          style={{ y: textY }}
        >
          <motion.h1
            className="font-heading text-5xl md:text-[64px] md:leading-[1.1] font-bold tracking-tighter max-w-[800px]"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          >
            Find Where the Grid Is{' '}
            <span className="text-[#B6F542]">Losing Power.</span>
          </motion.h1>

          <motion.p
            className="text-base md:text-lg text-[#9BA8A0] max-w-[600px] leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            Istikshaf combines grid physics, monthly billing records, smart-meter intelligence, and
            explainable AI to prioritize evidence-backed electricity-loss inspections.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 mt-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
          >
            <button
              onClick={() => navigate(ROUTES.WORKSPACES)}
              className="flex items-center justify-center bg-[#B6F542] text-[#11150a] px-8 py-4 rounded-md text-base font-semibold hover:bg-[#CAFF69] transition-all hover:scale-[1.02] shadow-[0_0_24px_rgba(182,245,66,0.15)]"
            >
              Launch Dashboard
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
            <a
              href="#how-it-works"
              className="flex items-center justify-center border border-[#263129] text-[#F3F7F4] px-8 py-4 rounded-md text-base font-medium hover:bg-[#161D19] transition-colors"
            >
              See How It Works
            </a>
          </motion.div>

          {/* Metrics bar */}
          <motion.div
            className="grid grid-cols-3 gap-8 mt-12 p-6 rounded-lg border border-[#263129] bg-[#0C0F06]/80 backdrop-blur-sm w-full max-w-[700px]"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="text-center border-r border-[#263129]">
              <AnimatedCounter value="30" color="#F3F7F4" label="Feeders" />
            </div>
            <div className="text-center border-r border-[#263129]">
              <AnimatedCounter value="300" color="#F3F7F4" label="PMTs" />
            </div>
            <div className="text-center">
              <AnimatedCounter value="10,000" color="#F3F7F4" label="Connections" />
            </div>
          </motion.div>

          <motion.p
            className="text-xs text-[#8c947c] italic"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
          >
            Synthetic demonstration network
          </motion.p>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 hidden md:block"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <ChevronDown className="w-6 h-6 text-[#9BA8A0] opacity-50" />
        </motion.div>
      </section>

      {/* ══════════════════════════════════════════════════
          HOW IT WORKS — 4-step pipeline
         ══════════════════════════════════════════════════ */}
      <section id="how-it-works" className="py-24 px-6 bg-[#0C110E] border-t border-[#263129]">
        <div className="max-w-[1200px] mx-auto">
          <ScrollReveal>
            <h2 className="font-heading text-3xl font-semibold text-[#F3F7F4] mb-3">
              How It Works
            </h2>
            <p className="text-base text-[#9BA8A0] max-w-2xl mb-16">
              A systematic approach to identifying and verifying technical vs. non-technical grid losses.
            </p>
          </ScrollReveal>

          <StaggerContainer className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {steps.map((s) => (
              <motion.div
                key={s.num}
                variants={staggerChild}
                className="bg-[#070A09] border border-[#263129] rounded-lg p-6 relative group hover:border-[#B6F542]/30 transition-colors"
              >
                <div className="absolute top-0 right-0 p-4 font-mono-tech text-sm text-[#8c947c]">
                  {s.num}
                </div>
                <div className="w-12 h-12 bg-[#161D19] rounded-full flex items-center justify-center mb-6 text-[#F3F7F4] group-hover:text-[#B6F542] transition-colors">
                  {s.icon}
                </div>
                <h3 className="font-heading text-lg font-semibold text-[#F3F7F4] mb-2">
                  {s.title}
                </h3>
                <p className="text-xs text-[#9BA8A0] leading-relaxed">{s.desc}</p>
              </motion.div>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════
          CORE CAPABILITIES — 4 feature cards
         ══════════════════════════════════════════════════ */}
      <section id="capabilities" className="py-24 px-6 bg-[#070A09] border-t border-[#263129]">
        <div className="max-w-[1200px] mx-auto">
          <ScrollReveal>
            <h2 className="font-heading text-3xl font-semibold text-[#F3F7F4] mb-3">
              Core Capabilities
            </h2>
            <p className="text-base text-[#9BA8A0] max-w-2xl mb-16">
              Advanced analytical tools for utility operators.
            </p>
          </ScrollReveal>

          <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {capabilities.map((cap) => (
              <motion.div
                key={cap.code}
                variants={staggerChild}
                className="border border-[#263129] rounded-lg bg-[#0C110E] overflow-hidden flex flex-col md:flex-row group hover:border-[#434935] transition-colors"
              >
                <div className="md:w-1/3 bg-[#161D19] flex items-center justify-center p-8 border-r border-[#263129]">
                  <Activity
                    className="w-16 h-16 text-[#9BA8A0] group-hover:text-[#F3F7F4] transition-colors"
                    style={{ color: undefined }}
                  />
                </div>
                <div className="p-6 md:w-2/3">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-heading text-lg font-semibold text-[#F3F7F4]">
                      {cap.title}
                    </h3>
                    <span className="font-mono-tech text-sm text-[#8c947c]">{cap.code}</span>
                  </div>
                  <p className="text-xs text-[#9BA8A0] leading-relaxed">{cap.desc}</p>
                  <div className="mt-4 h-[3px] rounded-full overflow-hidden bg-[#161D19]">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: cap.color }}
                      initial={{ width: 0 }}
                      whileInView={{ width: '100%' }}
                      viewport={{ once: true }}
                      transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════
          RESPONSIBLE USE MANDATE
         ══════════════════════════════════════════════════ */}
      <section
        id="responsible-use"
        className="py-24 px-6 bg-[#0C0F06] border-t border-[#263129] relative overflow-hidden"
      >
        {/* Grid texture overlay */}
        <div
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            backgroundSize: '40px 40px',
            backgroundImage:
              'linear-gradient(to right, rgba(140,148,124,0.3) 1px, transparent 1px), linear-gradient(to bottom, rgba(140,148,124,0.3) 1px, transparent 1px)',
          }}
        />

        <ScrollReveal className="max-w-[800px] mx-auto relative z-10">
          <div className="border border-[#263129] rounded-xl bg-[#11150a] p-8 shadow-[0_16px_32px_rgba(0,0,0,0.4)]">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 rounded-lg bg-[#B6F542]/10 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-[#B6F542]" />
              </div>
              <h2 className="font-heading text-2xl font-semibold text-[#F3F7F4]">
                Responsible Use Mandate
              </h2>
            </div>

            <p className="font-heading text-lg text-[#F3F7F4] mb-6 border-l-4 border-[#B6F542] pl-4">
              Istikshaf supports inspection decisions. It does not determine guilt.
            </p>

            <div className="space-y-4 text-sm text-[#9BA8A0]">
              <p>
                {RESPONSIBLE_TERMINOLOGY.SYSTEM_DISCLAIMER}
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>
                  <strong className="text-[#F3F7F4]">Solar Prosumer Protection:</strong> Algorithms
                  automatically adjust for bidirectional flows to prevent misflagging legitimate solar
                  generation.
                </li>
                <li>
                  <strong className="text-[#F3F7F4]">Outage Normalization:</strong> Missing data
                  periods are identified and isolated to prevent skewed statistical baselines.
                </li>
                <li>
                  <strong className="text-[#F3F7F4]">Field Verification Requirement:</strong> All
                  AI-flagged anomalies require physical inspection by certified personnel before
                  administrative action.
                </li>
              </ul>
            </div>

            {/* Terminology boxes */}
            <div className="grid grid-cols-2 gap-4 mt-6 text-xs font-mono-tech">
              <div className="p-4 rounded-lg bg-[#070A09] border border-[#263129] space-y-2">
                <span className="text-[#63D98A] font-bold block">✓ Responsible Terminology:</span>
                <ul className="text-[#9BA8A0] space-y-1">
                  <li>• Calibrated anomaly risk</li>
                  <li>• Unaccounted residual</li>
                  <li>• Potential non-technical loss pattern</li>
                  <li>• Recommended for field review</li>
                </ul>
              </div>
              <div className="p-4 rounded-lg bg-[#070A09] border border-[#263129] space-y-2">
                <span className="text-[#FF6262] font-bold block">✕ Prohibited Terminology:</span>
                <ul className="text-[#9BA8A0] space-y-1">
                  <li>• Thief detected / Theft confirmed</li>
                  <li>• Guilty / Chance of theft</li>
                  <li>• Suspicious house</li>
                  <li>• Criminal intent</li>
                </ul>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* ══════════════════════════════════════════════════
          FOOTER
         ══════════════════════════════════════════════════ */}
      <footer className="bg-[#161D19] border-t border-[#263129] py-12 px-6">
        <div className="max-w-[1200px] mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-[#B6F542]" />
              <span className="font-heading text-xl font-semibold text-[#F3F7F4] tracking-tight">
                Istikshaf
              </span>
            </div>
            <p className="text-xs text-[#9BA8A0] max-w-sm">
              Utility Ops AI. Precise, Industrial, and Vigilant.
            </p>
          </div>
          <div>
            <h4 className="text-[11px] uppercase tracking-[0.05em] font-bold text-[#9BA8A0] mb-4">
              Platform
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to={ROUTES.ANALYST.ROOT} className="text-[#8c947c] hover:text-[#F3F7F4] transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to={ROUTES.ANALYST.GRID} className="text-[#8c947c] hover:text-[#F3F7F4] transition-colors">
                  Grid Topology
                </Link>
              </li>
              <li>
                <Link to={ROUTES.ANALYST.INVESTIGATIONS} className="text-[#8c947c] hover:text-[#F3F7F4] transition-colors">
                  Analytics
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-[11px] uppercase tracking-[0.05em] font-bold text-[#9BA8A0] mb-4">
              Legal
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="#" className="text-[#8c947c] hover:text-[#F3F7F4] transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-[#8c947c] hover:text-[#F3F7F4] transition-colors">
                  Terms of Service
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="max-w-[1200px] mx-auto mt-12 pt-8 border-t border-[#263129]/50 text-center text-xs text-[#8c947c]">
          © 2024 Istikshaf Grid Monitor. All rights reserved.
        </div>
      </footer>
    </div>
  );
};
