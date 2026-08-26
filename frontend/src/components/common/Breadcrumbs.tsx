import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { ROUTES } from '../../config/routes';

interface BreadcrumbsProps {
  customItems?: Array<{ label: string; href?: string }>;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ customItems }) => {
  const location = useLocation();

  if (customItems) {
    return (
      <nav aria-label="Breadcrumb" className="no-print flex items-center gap-1.5 text-xs text-[#9BA8A0] mb-4">
        <Link to={ROUTES.HOME} className="hover:text-[#B6F542] transition-colors flex items-center gap-1">
          <Home className="w-3.5 h-3.5" />
          <span>Home</span>
        </Link>
        {customItems.map((item, idx) => (
          <React.Fragment key={idx}>
            <ChevronRight className="w-3.5 h-3.5 text-[#263129]" />
            {item.href ? (
              <Link to={item.href} className="hover:text-[#B6F542] transition-colors">
                {item.label}
              </Link>
            ) : (
              <span className="font-semibold text-[#F3F7F4] font-mono-tech">{item.label}</span>
            )}
          </React.Fragment>
        ))}
      </nav>
    );
  }

  const pathnames = location.pathname.split('/').filter((x) => x);

  return (
    <nav aria-label="Breadcrumb" className="no-print flex items-center gap-1.5 text-xs text-[#9BA8A0] mb-4">
      <Link to={ROUTES.HOME} className="hover:text-[#B6F542] transition-colors flex items-center gap-1">
        <Home className="w-3.5 h-3.5" />
        <span>Home</span>
      </Link>

      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <React.Fragment key={to}>
            <ChevronRight className="w-3.5 h-3.5 text-[#263129]" />
            {isLast ? (
              <span className="font-semibold text-[#F3F7F4] capitalize font-mono-tech">{value.replace('-', ' ')}</span>
            ) : (
              <Link to={to} className="hover:text-[#B6F542] transition-colors capitalize">
                {value.replace('-', ' ')}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
