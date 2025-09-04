import React, { useState } from 'react';
import clsx from 'clsx';
import type { SearchResult } from '../../types';

interface ResultCardProps {
  result: SearchResult;
  isSelected?: boolean;
  onClick?: () => void;
  onMouseEnter?: () => void;
  onCopy?: (text: string) => void;
  onFavorite?: (result: SearchResult) => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({
  result,
  isSelected = false,
  onClick,
  onMouseEnter,
  onCopy,
  onFavorite
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  const handleCopy = (e: React.MouseEvent, text: string) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    onCopy?.(text);
  };

  const handleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFavorite?.(result);
  };

  const formatPartOfSpeech = (pos: string): string => {
    const posMap: Record<string, string> = {
      'n': 'noun',
      'v': 'verb',
      'adj': 'adjective',
      'adv': 'adverb',
      'prep': 'preposition',
      'conj': 'conjunction',
      'int': 'interjection',
      'pron': 'pronoun',
      'det': 'determiner'
    };
    return posMap[pos.toLowerCase()] || pos;
  };

  // const truncateText = (text: string, maxLength: number): string => {
  //   if (text.length <= maxLength) return text;
  //   return text.substring(0, maxLength) + '...';
  // };

  return (
    <div
      className={clsx(
        'p-4 cursor-pointer transition-all duration-200 rounded-lg',
        'border border-transparent hover:border-blue-200 hover:shadow-sm',
        {
          'border-blue-500 bg-blue-50 shadow-sm': isSelected,
          'hover:bg-gray-50': !isSelected
        }
      )}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
    >
      {/* Main Content */}
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3">
              <h3 className="text-lg font-semibold text-gray-900">
                {result.lemma}
              </h3>
              
              {result.pos && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {formatPartOfSpeech(result.pos)}
                </span>
              )}

              {result.frequency && (
                <span className="text-xs text-gray-500">
                  freq: {result.frequency.toLocaleString()}
                </span>
              )}
            </div>

            {/* Pronunciation */}
            {result.pronunciation && (
              <div className="mt-1 text-sm text-gray-600">
                /{result.pronunciation}/
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-1 ml-4">
            <button
              onClick={(e) => handleCopy(e, result.lemma)}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              title="Copy word"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
            
            <button
              onClick={handleFavorite}
              className="p-1.5 text-gray-400 hover:text-yellow-500 hover:bg-yellow-50 rounded-md transition-colors"
              title="Add to favorites"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </button>

            <button
              onClick={handleToggleExpand}
              className={clsx(
                'p-1.5 rounded-md transition-all duration-200',
                'text-gray-400 hover:text-gray-600 hover:bg-gray-100',
                {
                  'transform rotate-180': isExpanded
                }
              )}
              title={isExpanded ? "Show less" : "Show more"}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Definition */}
        <div className="text-gray-700">
          <p className={clsx({
            'line-clamp-2': !isExpanded
          })}>
            {result.definition}
          </p>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="space-y-3 pt-2 border-t border-gray-100 animate-slide-up">
            {/* Example */}
            {result.example && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Example</h4>
                <p className="text-sm text-gray-600 italic">
                  "{result.example}"
                </p>
              </div>
            )}

            {/* Etymology */}
            {result.etymology && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Etymology</h4>
                <p className="text-sm text-gray-600">
                  {result.etymology}
                </p>
              </div>
            )}

            {/* Usage Notes */}
            {result.usage_notes && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Usage</h4>
                <p className="text-sm text-gray-600">
                  {result.usage_notes}
                </p>
              </div>
            )}

            {/* Related Words */}
            <div className="space-y-2">
              {result.synonyms && result.synonyms.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Synonyms</h4>
                  <div className="flex flex-wrap gap-1">
                    {result.synonyms.map((synonym, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-green-50 text-green-700 hover:bg-green-100 cursor-pointer transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Could trigger new search for synonym
                        }}
                      >
                        {synonym}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {result.antonyms && result.antonyms.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Antonyms</h4>
                  <div className="flex flex-wrap gap-1">
                    {result.antonyms.map((antonym, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-red-50 text-red-700 hover:bg-red-100 cursor-pointer transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Could trigger new search for antonym
                        }}
                      >
                        {antonym}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {result.inflections && result.inflections.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Word Forms</h4>
                  <div className="flex flex-wrap gap-1">
                    {result.inflections.map((inflection, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 cursor-pointer transition-colors"
                      >
                        {inflection}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};