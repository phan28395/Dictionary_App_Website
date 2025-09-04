import React, { useRef, useState, useEffect } from 'react';
import clsx from 'clsx';
import type { SearchBarProps, Suggestion } from '../../types';

interface SuggestionItemProps {
  suggestion: Suggestion;
  isSelected: boolean;
  onSelect: () => void;
  onHover: () => void;
}

const SuggestionItem: React.FC<SuggestionItemProps> = ({
  suggestion,
  isSelected,
  onSelect,
  onHover
}) => (
  <button
    type="button"
    className={clsx(
      'w-full px-3 py-2 text-left text-sm transition-colors duration-150',
      'flex items-center justify-between',
      'hover:bg-blue-50 focus:bg-blue-50 focus:outline-none',
      {
        'bg-blue-100 text-blue-900': isSelected,
        'text-gray-700': !isSelected
      }
    )}
    onClick={onSelect}
    onMouseEnter={onHover}
    role="option"
    aria-selected={isSelected}
  >
    <span className="font-medium">{suggestion.word}</span>
    {suggestion.frequency && (
      <span className="text-xs text-gray-500 ml-2">
        {suggestion.frequency.toLocaleString()}
      </span>
    )}
  </button>
);

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSubmit,
  onFocus,
  onBlur,
  placeholder = "Search dictionary...",
  className,
  isLoading = false,
  suggestions = [],
  onSuggestionSelect
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Show suggestions when there are suggestions and input is focused
  useEffect(() => {
    setShowSuggestions(isFocused && suggestions.length > 0 && value.trim().length > 0);
  }, [isFocused, suggestions.length, value]);

  // Reset selected suggestion when suggestions change
  useEffect(() => {
    setSelectedSuggestionIndex(-1);
  }, [suggestions]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setSelectedSuggestionIndex(-1);
  };

  const handleInputFocus = () => {
    setIsFocused(true);
    onFocus?.();
  };

  const handleInputBlur = (_e: React.FocusEvent<HTMLInputElement>) => {
    // Delay hiding suggestions to allow clicks on suggestions
    setTimeout(() => {
      setIsFocused(false);
      setShowSuggestions(false);
      setSelectedSuggestionIndex(-1);
    }, 150);
    onBlur?.();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // If a suggestion is selected, use it
    if (selectedSuggestionIndex >= 0 && selectedSuggestionIndex < suggestions.length) {
      const selectedSuggestion = suggestions[selectedSuggestionIndex];
      onChange(selectedSuggestion.word);
      onSuggestionSelect?.(selectedSuggestion.word);
      onSubmit(selectedSuggestion.word);
    } else {
      onSubmit(value);
    }
    
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    inputRef.current?.blur();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) {
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => prev > -1 ? prev - 1 : -1);
        break;
      
      case 'Escape':
        e.preventDefault();
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
        inputRef.current?.blur();
        break;
        
      case 'Tab':
        // Allow tab to close suggestions
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
        break;
    }
  };

  const selectSuggestion = (suggestion: Suggestion, _index: number) => {
    onChange(suggestion.word);
    onSuggestionSelect?.(suggestion.word);
    onSubmit(suggestion.word);
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
  };

  const clearInput = () => {
    onChange('');
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    inputRef.current?.focus();
  };

  return (
    <div className={clsx('relative w-full', className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          {/* Search Icon */}
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          {/* Input Field */}
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onBlur={handleInputBlur}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={clsx(
              'w-full pl-10 pr-20 py-3 text-base',
              'border border-gray-300 rounded-lg',
              'bg-white text-gray-900 placeholder-gray-500',
              'focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50',
              'transition-colors duration-200',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
            disabled={isLoading}
            autoComplete="off"
            spellCheck="false"
            role="combobox"
            aria-expanded={showSuggestions}
            aria-haspopup="listbox"
            aria-autocomplete="list"
          />

          {/* Loading Spinner */}
          {isLoading && (
            <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
            </div>
          )}

          {/* Clear Button */}
          {value && !isLoading && (
            <button
              type="button"
              onClick={clearInput}
              className={clsx(
                'absolute right-3 top-1/2 transform -translate-y-1/2',
                'p-1 rounded-full text-gray-400 hover:text-gray-600',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50',
                'transition-colors duration-200'
              )}
              aria-label="Clear search"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Submit button (hidden, triggered by Enter) */}
        <button type="submit" className="hidden" aria-hidden="true" />
      </form>

      {/* Suggestions Popover */}
      {showSuggestions && (
        <div
          ref={suggestionsRef}
          className={clsx(
            'absolute top-full left-0 right-0 z-50 mt-1',
            'bg-white border border-gray-200 rounded-lg shadow-popup',
            'max-h-64 overflow-y-auto',
            'animate-fade-in'
          )}
          role="listbox"
          aria-label="Search suggestions"
        >
          {suggestions.map((suggestion, index) => (
            <SuggestionItem
              key={`${suggestion.word}-${index}`}
              suggestion={suggestion}
              isSelected={selectedSuggestionIndex === index}
              onSelect={() => selectSuggestion(suggestion, index)}
              onHover={() => setSelectedSuggestionIndex(index)}
            />
          ))}
          
          {/* Footer with hint */}
          <div className="px-3 py-2 text-xs text-gray-500 border-t border-gray-100 bg-gray-50">
            <div className="flex items-center justify-between">
              <span>Use ↑↓ to navigate, Enter to select</span>
              <span>ESC to close</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};