import React, { useRef, useEffect, useState } from 'react';
import { ScrollArea } from '@radix-ui/react-scroll-area';
import clsx from 'clsx';
import type { SearchResultsProps, SearchResult } from '../../types';
import { ResultCard } from './ResultCard';

interface VirtualScrollProps {
  items: SearchResult[];
  itemHeight: number;
  containerHeight: number;
  selectedIndex?: number;
  onResultSelect?: (result: SearchResult, index: number) => void;
  onResultHover?: (index: number) => void;
  renderBuffer?: number;
}

const VirtualScrollList: React.FC<VirtualScrollProps> = ({
  items,
  itemHeight,
  containerHeight,
  selectedIndex,
  onResultSelect,
  onResultHover,
  renderBuffer = 5
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef<HTMLDivElement>(null);

  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const totalHeight = items.length * itemHeight;
  
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - renderBuffer);
  const endIndex = Math.min(items.length, startIndex + visibleCount + renderBuffer * 2);
  
  const visibleItems = items.slice(startIndex, endIndex);
  const offsetY = startIndex * itemHeight;

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  // Scroll to selected item
  useEffect(() => {
    if (selectedIndex !== undefined && selectedIndex >= 0 && scrollElementRef.current) {
      const selectedItemTop = selectedIndex * itemHeight;
      const selectedItemBottom = selectedItemTop + itemHeight;
      const currentScrollTop = scrollTop;
      const currentScrollBottom = scrollTop + containerHeight;

      if (selectedItemTop < currentScrollTop) {
        scrollElementRef.current.scrollTop = selectedItemTop;
      } else if (selectedItemBottom > currentScrollBottom) {
        scrollElementRef.current.scrollTop = selectedItemBottom - containerHeight;
      }
    }
  }, [selectedIndex, itemHeight, containerHeight, scrollTop]);

  return (
    <div
      ref={scrollElementRef}
      className="h-full overflow-auto"
      onScroll={handleScroll}
      style={{ height: containerHeight }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map((item, index) => {
            const actualIndex = startIndex + index;
            return (
              <div
                key={`${item.id}-${actualIndex}`}
                style={{ height: itemHeight }}
                className="px-1"
              >
                <ResultCard
                  result={item}
                  isSelected={selectedIndex === actualIndex}
                  onClick={() => onResultSelect?.(item, actualIndex)}
                  onMouseEnter={() => onResultHover?.(actualIndex)}
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  selectedIndex = -1,
  onResultSelect,
  onResultHover,
  className,
  maxHeight = 400
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [useVirtualScrolling, setUseVirtualScrolling] = useState(false);

  // Enable virtual scrolling for large result sets
  useEffect(() => {
    setUseVirtualScrolling(results.length > 20);
  }, [results.length]);

  if (results.length === 0) {
    return (
      <div className={clsx('text-center py-8 text-gray-500', className)}>
        <div className="flex flex-col items-center">
          <svg className="w-12 h-12 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-sm text-gray-500">
            Try different keywords or check your spelling
          </p>
        </div>
      </div>
    );
  }

  const itemHeight = 120; // Approximate height of a ResultCard

  return (
    <div
      ref={containerRef}
      className={clsx(
        'bg-white border border-gray-200 rounded-lg shadow-sm',
        'animate-fade-in',
        className
      )}
      style={{ maxHeight }}
    >
      {/* Results Header */}
      <div className="px-4 py-3 border-b border-gray-100 bg-gray-50 rounded-t-lg">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-gray-900">
            {results.length} result{results.length !== 1 ? 's' : ''} found
          </h2>
          <div className="text-xs text-gray-500">
            Use ↑↓ to navigate, Enter to select
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="relative">
        {useVirtualScrolling ? (
          <VirtualScrollList
            items={results}
            itemHeight={itemHeight}
            containerHeight={maxHeight - 60} // Subtract header height
            selectedIndex={selectedIndex}
            onResultSelect={onResultSelect}
            onResultHover={onResultHover}
          />
        ) : (
          <ScrollArea className="h-full">
            <div 
              className="divide-y divide-gray-100"
              style={{ maxHeight: maxHeight - 60 }}
            >
              {results.map((result, index) => (
                <div key={`${result.id}-${index}`} className="px-1">
                  <ResultCard
                    result={result}
                    isSelected={selectedIndex === index}
                    onClick={() => onResultSelect?.(result, index)}
                    onMouseEnter={() => onResultHover?.(index)}
                  />
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </div>

      {/* Results Footer */}
      {results.length > 0 && (
        <div className="px-4 py-2 border-t border-gray-100 bg-gray-50 rounded-b-lg">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>
              {selectedIndex >= 0 ? `${selectedIndex + 1} of ${results.length}` : `${results.length} total`}
            </span>
            <span>
              Press Ctrl+K to search again
            </span>
          </div>
        </div>
      )}
    </div>
  );
};