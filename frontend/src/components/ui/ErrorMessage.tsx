import React from 'react';

interface ErrorMessageProps {
  message: string | null;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, className = "" }) => {
  if (!message) return null;

  return (
    <div className={`bg-red-900/50 border border-red-500 rounded-lg p-4 ${className}`}>
      <p className="text-red-200">{message}</p>
    </div>
  );
};