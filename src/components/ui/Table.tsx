import React from 'react';

interface Column {
  key: string;
  label: string;
  align?: 'left' | 'center' | 'right';
  className?: string;
}

interface TableProps {
  columns: Column[];
  data: Record<string, any>[];
  className?: string;
  emptyMessage?: string;
}

export const Table: React.FC<TableProps> = ({ 
  columns, 
  data, 
  className = '',
  emptyMessage = 'No data available'
}) => {
  if (data.length === 0) {
    return (
      <div className="text-center text-secondary-400 py-8">
        {emptyMessage}
      </div>
    );
  }

  const getAlignClass = (align: string = 'left') => {
    switch (align) {
      case 'center': return 'text-center';
      case 'right': return 'text-right';
      default: return 'text-left';
    }
  };

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-secondary-600">
            {columns.map((column) => (
              <th 
                key={column.key}
                className={`py-2 text-secondary-400 font-medium ${getAlignClass(column.align)} ${column.className || ''}`}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} className="border-b border-secondary-700/50">
              {columns.map((column) => (
                <td 
                  key={column.key}
                  className={`py-2 ${getAlignClass(column.align)} ${column.className || ''}`}
                >
                  {row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

interface SimpleTableProps {
  headers: string[];
  rows: (string | number | React.ReactNode)[][];
  className?: string;
}

export const SimpleTable: React.FC<SimpleTableProps> = ({ 
  headers, 
  rows, 
  className = '' 
}) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-secondary-700">
            {headers.map((header, index) => (
              <th key={index} className="text-left text-secondary-300 font-medium py-2">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="border-b border-secondary-800">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="py-2 text-white">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};