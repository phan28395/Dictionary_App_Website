import { PluginManifest, DictionaryTerm } from './types';

// Plugin manifest validation
export function validatePluginManifest(manifest: any): manifest is PluginManifest {
  if (!manifest || typeof manifest !== 'object') {
    return false;
  }

  const required = ['id', 'name', 'version', 'main'];
  for (const field of required) {
    if (!manifest[field] || typeof manifest[field] !== 'string') {
      return false;
    }
  }

  if (manifest.permissions && !Array.isArray(manifest.permissions)) {
    return false;
  }

  if (manifest.dependencies && typeof manifest.dependencies !== 'object') {
    return false;
  }

  return true;
}

// Text processing utilities
export class TextUtils {
  /**
   * Highlight search term in text
   */
  static highlightText(text: string, searchTerm: string, className = 'highlight'): string {
    if (!searchTerm || !text) return text;
    
    const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
    return text.replace(regex, `<span class="${className}">$1</span>`);
  }

  /**
   * Truncate text to specified length
   */
  static truncateText(text: string, maxLength: number, suffix = '...'): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - suffix.length) + suffix;
  }

  /**
   * Clean and normalize search terms
   */
  static normalizeSearchTerm(term: string): string {
    return term
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '') // Remove special chars except hyphens
      .replace(/\s+/g, ' '); // Normalize whitespace
  }

  /**
   * Extract key terms from definition
   */
  static extractKeywords(text: string, maxWords = 5): string[] {
    const stopWords = new Set([
      'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
      'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
      'to', 'was', 'will', 'with', 'or', 'but', 'not', 'this', 'they'
    ]);

    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2 && !stopWords.has(word))
      .slice(0, maxWords);
  }
}

// Dictionary term utilities
export class DictionaryUtils {
  /**
   * Format part of speech
   */
  static formatPOS(pos: string): string {
    const posMap: Record<string, string> = {
      'n': 'noun',
      'v': 'verb',
      'adj': 'adjective',
      'adv': 'adverb',
      'prep': 'preposition',
      'conj': 'conjunction',
      'int': 'interjection',
      'pron': 'pronoun',
      'det': 'determiner',
    };
    
    return posMap[pos.toLowerCase()] || pos;
  }

  /**
   * Group terms by part of speech
   */
  static groupByPOS(terms: DictionaryTerm[]): Record<string, DictionaryTerm[]> {
    const groups: Record<string, DictionaryTerm[]> = {};
    
    for (const term of terms) {
      const pos = term.pos || 'unknown';
      if (!groups[pos]) {
        groups[pos] = [];
      }
      groups[pos].push(term);
    }
    
    return groups;
  }

  /**
   * Sort terms by frequency and relevance
   */
  static sortTerms(terms: DictionaryTerm[], searchTerm?: string): DictionaryTerm[] {
    return terms.sort((a, b) => {
      // Exact matches first
      if (searchTerm) {
        const aExact = a.lemma.toLowerCase() === searchTerm.toLowerCase();
        const bExact = b.lemma.toLowerCase() === searchTerm.toLowerCase();
        if (aExact && !bExact) return -1;
        if (!aExact && bExact) return 1;
      }
      
      // Then by frequency
      return (b.frequency || 0) - (a.frequency || 0);
    });
  }

  /**
   * Calculate term relevance score
   */
  static calculateRelevance(term: DictionaryTerm, searchTerm: string): number {
    const lemma = term.lemma.toLowerCase();
    const search = searchTerm.toLowerCase();
    
    let score = 0;
    
    // Exact match gets highest score
    if (lemma === search) score += 100;
    
    // Starts with search term
    if (lemma.startsWith(search)) score += 50;
    
    // Contains search term
    if (lemma.includes(search)) score += 25;
    
    // Frequency bonus (normalized to 0-25)
    score += Math.min((term.frequency || 0) / 1000, 25);
    
    // Length penalty (shorter words are often more relevant)
    score -= lemma.length * 0.5;
    
    return Math.max(score, 0);
  }
}

// Plugin development utilities
export class PluginDevUtils {
  /**
   * Create a debounced function
   */
  static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }

  /**
   * Create a throttled function
   */
  static throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  /**
   * Generate unique ID
   */
  static generateId(): string {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  }

  /**
   * Deep clone object
   */
  static deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj) as any;
    if (obj instanceof Array) return obj.map(item => this.deepClone(item)) as any;
    if (typeof obj === 'object') {
      const copy = {} as any;
      Object.keys(obj).forEach(key => {
        copy[key] = this.deepClone((obj as any)[key]);
      });
      return copy;
    }
    return obj;
  }

  /**
   * Format file size
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Parse semantic version
   */
  static parseVersion(version: string): { major: number; minor: number; patch: number } {
    const parts = version.split('.').map(Number);
    return {
      major: parts[0] || 0,
      minor: parts[1] || 0,
      patch: parts[2] || 0,
    };
  }

  /**
   * Compare semantic versions
   */
  static compareVersions(a: string, b: string): number {
    const versionA = this.parseVersion(a);
    const versionB = this.parseVersion(b);
    
    if (versionA.major !== versionB.major) return versionA.major - versionB.major;
    if (versionA.minor !== versionB.minor) return versionA.minor - versionB.minor;
    return versionA.patch - versionB.patch;
  }
}

// Helper function for regex escaping
function escapeRegExp(string: string): string {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}