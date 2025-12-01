import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  className = "",
  ...props
}) => (
  <div className="mb-2 text-left">
    {label && (
      <label
        htmlFor={props.id || props.name}
        className="block text-sm font-medium text-base-content mb-1"
      >
        {label}
      </label>
    )}
    <input
      className={
        "block w-full px-4 py-2 border border-secondary-600 rounded-lg bg-secondary-700 placeholder-secondary-200 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary transition " +
        className
      }
      {...props}
    />
    {error && <div className="text-xs text-red-400 mt-1">{error}</div>}
  </div>
);