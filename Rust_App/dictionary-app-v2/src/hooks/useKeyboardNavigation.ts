import { useEffect, useCallback, useRef } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

interface KeyboardNavigationOptions {
  enabled?: boolean;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onEnter?: () => void;
  onEscape?: () => void;
  onHome?: () => void;
  onEnd?: () => void;
  onPageUp?: () => void;
  onPageDown?: () => void;
  onTab?: () => void;
  onShiftTab?: () => void;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  scopes?: string[];
}

export const useKeyboardNavigation = ({
  enabled = true,
  onArrowUp,
  onArrowDown,
  onEnter,
  onEscape,
  onHome,
  onEnd,
  onPageUp,
  onPageDown,
  onTab,
  onShiftTab,
  preventDefault = true,
  stopPropagation = true,
  scopes = ['navigation']
}: KeyboardNavigationOptions = {}) => {
  
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    let handled = false;

    switch (event.key) {
      case 'ArrowUp':
        onArrowUp?.();
        handled = true;
        break;
      case 'ArrowDown':
        onArrowDown?.();
        handled = true;
        break;
      case 'Enter':
        onEnter?.();
        handled = true;
        break;
      case 'Escape':
        onEscape?.();
        handled = true;
        break;
      case 'Home':
        onHome?.();
        handled = true;
        break;
      case 'End':
        onEnd?.();
        handled = true;
        break;
      case 'PageUp':
        onPageUp?.();
        handled = true;
        break;
      case 'PageDown':
        onPageDown?.();
        handled = true;
        break;
      case 'Tab':
        if (event.shiftKey) {
          onShiftTab?.();
        } else {
          onTab?.();
        }
        handled = true;
        break;
    }

    if (handled && preventDefault) {
      event.preventDefault();
    }
    if (handled && stopPropagation) {
      event.stopPropagation();
    }
  }, [
    enabled,
    onArrowUp,
    onArrowDown,
    onEnter,
    onEscape,
    onHome,
    onEnd,
    onPageUp,
    onPageDown,
    onTab,
    onShiftTab,
    preventDefault,
    stopPropagation
  ]);

  // Register hotkeys using react-hotkeys-hook
  useHotkeys('up', onArrowUp || (() => {}), { enabled, scopes });
  useHotkeys('down', onArrowDown || (() => {}), { enabled, scopes });
  useHotkeys('enter', onEnter || (() => {}), { enabled, scopes });
  useHotkeys('escape', onEscape || (() => {}), { enabled, scopes });
  useHotkeys('home', onHome || (() => {}), { enabled, scopes });
  useHotkeys('end', onEnd || (() => {}), { enabled, scopes });
  useHotkeys('pageup', onPageUp || (() => {}), { enabled, scopes });
  useHotkeys('pagedown', onPageDown || (() => {}), { enabled, scopes });
  useHotkeys('tab', onTab || (() => {}), { enabled, scopes }); 
  useHotkeys('shift+tab', onShiftTab || (() => {}), { enabled, scopes });

  return {
    handleKeyDown
  };
};

// Hook for managing focus within a container
export const useFocusManagement = (containerRef: React.RefObject<HTMLElement>) => {
  const focusableElements = useRef<HTMLElement[]>([]);

  const updateFocusableElements = useCallback(() => {
    if (!containerRef.current) return;

    const selectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'textarea:not([disabled])',
      'select:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[role="button"]',
      '[role="link"]',
      '[role="menuitem"]'
    ];

    const elements = Array.from(
      containerRef.current.querySelectorAll(selectors.join(','))
    ) as HTMLElement[];

    focusableElements.current = elements.filter(el => {
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden';
    });
  }, [containerRef]);

  const focusFirst = useCallback(() => {
    updateFocusableElements();
    if (focusableElements.current[0]) {
      focusableElements.current[0].focus();
    }
  }, [updateFocusableElements]);

  const focusLast = useCallback(() => {
    updateFocusableElements();
    const elements = focusableElements.current;
    if (elements[elements.length - 1]) {
      elements[elements.length - 1].focus();
    }
  }, [updateFocusableElements]);

  const focusNext = useCallback(() => {
    updateFocusableElements();
    const currentIndex = focusableElements.current.findIndex(
      el => el === document.activeElement
    );
    const nextIndex = (currentIndex + 1) % focusableElements.current.length;
    if (focusableElements.current[nextIndex]) {
      focusableElements.current[nextIndex].focus();
    }
  }, [updateFocusableElements]);

  const focusPrevious = useCallback(() => {
    updateFocusableElements();
    const currentIndex = focusableElements.current.findIndex(
      el => el === document.activeElement
    );
    const prevIndex = currentIndex === 0 
      ? focusableElements.current.length - 1 
      : currentIndex - 1;
    if (focusableElements.current[prevIndex]) {
      focusableElements.current[prevIndex].focus();
    }
  }, [updateFocusableElements]);

  const trapFocus = useCallback((event: KeyboardEvent) => {
    if (event.key !== 'Tab') return;

    updateFocusableElements();
    const elements = focusableElements.current;
    if (elements.length === 0) return;

    const firstElement = elements[0];
    const lastElement = elements[elements.length - 1];

    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }, [updateFocusableElements]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      trapFocus(event);
    };

    container.addEventListener('keydown', handleKeyDown);
    return () => container.removeEventListener('keydown', handleKeyDown);
  }, [containerRef, trapFocus]);

  return {
    focusFirst,
    focusLast,
    focusNext,
    focusPrevious,
    updateFocusableElements,
    getFocusableElements: () => focusableElements.current
  };
};

// Hook for global hotkeys (like Ctrl+Ctrl to open dictionary)
export const useGlobalHotkeys = () => {
  // Register global hotkey for opening dictionary (Ctrl+Ctrl)
  const registerOpenHotkey = useCallback((callback: () => void) => {
    let ctrlPressed = false;
    let ctrlCount = 0;
    let resetTimeout: NodeJS.Timeout;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Control') {
        if (!ctrlPressed) {
          ctrlPressed = true;
          ctrlCount++;
          
          clearTimeout(resetTimeout);
          resetTimeout = setTimeout(() => {
            ctrlCount = 0;
          }, 500); // Reset count after 500ms
          
          if (ctrlCount === 2) {
            callback();
            ctrlCount = 0;
          }
        }
      } else {
        ctrlCount = 0;
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      if (event.key === 'Control') {
        ctrlPressed = false;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
      clearTimeout(resetTimeout);
    };
  }, []);

  // Register Ctrl+K for search focus
  useHotkeys('ctrl+k', (event) => {
    event.preventDefault();
    const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }, { scopes: ['global'] });

  return {
    registerOpenHotkey
  };
};