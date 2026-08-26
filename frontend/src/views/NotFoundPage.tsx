import React from 'react';
import { Link } from 'react-router-dom';
import { Zap, Home, ArrowLeft } from 'lucide-react';
import { ROUTES } from '../config/routes';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#070A09] text-[#F3F7F4] font-sans flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-[#FF6262]/10 border border-[#FF6262]/30 text-[#FF6262] flex items-center justify-center font-extrabold mb-6">
        <Zap className="w-8 h-8" />
      </div>

      <h1 className="text-4xl font-extrabold font-heading text-[#F3F7F4] mb-2">404 — Grid Node Not Found</h1>
      <p className="text-xs text-[#9BA8A0] max-w-md mb-8">
        The requested grid route or consumer record does not exist in the active Istikshaf topology index.
      </p>

      <div className="flex items-center gap-4">
        <Link
          to={ROUTES.HOME}
          className="px-5 py-2.5 rounded-lg bg-[#B6F542] text-[#070A09] font-bold text-xs flex items-center gap-2 hover:bg-[#CAFF69] transition-all"
        >
          <Home className="w-4 h-4" />
          <span>Return Home</span>
        </Link>
        <Link
          to={ROUTES.ANALYST.ROOT}
          className="px-5 py-2.5 rounded-lg bg-[#161D19] text-[#F3F7F4] border border-[#263129] font-semibold text-xs flex items-center gap-2 hover:bg-[#263129] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Go to Analyst Overview</span>
        </Link>
      </div>
    </div>
  );
};
