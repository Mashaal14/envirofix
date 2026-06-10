import React from 'react';

const Logo = ({ size = 'medium', variant = 'color' }) => {
  const sizes = {
    small: 'w-6 h-6',
    medium: 'w-8 h-8',
    large: 'w-10 h-10',
    xl: 'w-12 h-12'
  };
  
  return (
    <img 
      src="/images/logo.png"
      alt="EnviroFix" 
      className={`${sizes[size]} object-contain`}
    />
  );
};

export default Logo;
