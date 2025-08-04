/**
 * Currency formatting and localization utilities
 * 
 * Provides comprehensive currency support for the business planning system
 * with proper formatting, validation, and internationalization.
 */

export type CurrencyCode = 'EUR' | 'USD' | 'GBP' | 'SEK' | 'NOK' | 'DKK';
export type LocaleCode = 'en-US' | 'en-GB' | 'nb-NO' | 'sv-SE' | 'da-DK' | 'de-DE';

export interface CurrencyConfig {
  code: CurrencyCode;
  symbol: string;
  name: string;
  locale: LocaleCode;
  decimalPlaces: number;
  thousandSeparator: string;
  decimalSeparator: string;
  symbolPosition: 'before' | 'after';
  spaceAfterSymbol: boolean;
}

export const CURRENCY_CONFIGS: Record<CurrencyCode, CurrencyConfig> = {
  EUR: {
    code: 'EUR',
    symbol: '€',
    name: 'Euro',
    locale: 'de-DE',
    decimalPlaces: 0, // Business planning typically uses whole currency units
    thousandSeparator: '.',
    decimalSeparator: ',',
    symbolPosition: 'after',
    spaceAfterSymbol: true
  },
  USD: {
    code: 'USD',
    symbol: '$',
    name: 'US Dollar',
    locale: 'en-US',
    decimalPlaces: 0,
    thousandSeparator: ',',
    decimalSeparator: '.',
    symbolPosition: 'before',
    spaceAfterSymbol: false
  },
  GBP: {
    code: 'GBP',
    symbol: '£',
    name: 'British Pound',
    locale: 'en-GB',
    decimalPlaces: 0,
    thousandSeparator: ',',
    decimalSeparator: '.',
    symbolPosition: 'before',
    spaceAfterSymbol: false
  },
  SEK: {
    code: 'SEK',
    symbol: 'kr',
    name: 'Swedish Krona',
    locale: 'sv-SE',
    decimalPlaces: 0,
    thousandSeparator: ' ',
    decimalSeparator: ',',
    symbolPosition: 'after',
    spaceAfterSymbol: true
  },
  NOK: {
    code: 'NOK',
    symbol: 'kr',
    name: 'Norwegian Krone',
    locale: 'nb-NO',
    decimalPlaces: 0,
    thousandSeparator: ' ',
    decimalSeparator: ',',
    symbolPosition: 'after',
    spaceAfterSymbol: true
  },
  DKK: {
    code: 'DKK',
    symbol: 'kr',
    name: 'Danish Krone',
    locale: 'da-DK',
    decimalPlaces: 0,
    thousandSeparator: '.',
    decimalSeparator: ',',
    symbolPosition: 'after',
    spaceAfterSymbol: true
  }
};

export class CurrencyFormatter {
  private config: CurrencyConfig;
  
  constructor(currencyCode: CurrencyCode = 'EUR') {
    this.config = CURRENCY_CONFIGS[currencyCode];
  }

  /**
   * Format a number as currency according to the configured locale and format
   */
  format(amount: number, options?: {
    precision?: number;
    showSymbol?: boolean;
    compact?: boolean;
    useLocaleFormatting?: boolean;
  }): string {
    const {
      precision = this.config.decimalPlaces,
      showSymbol = true,
      compact = false,
      useLocaleFormatting = true
    } = options || {};

    // Handle compact formatting (e.g., "€1.2M", "€850K")
    if (compact && Math.abs(amount) >= 1000) {
      return this.formatCompact(amount, showSymbol);
    }

    let formattedNumber: string;

    if (useLocaleFormatting) {
      // Use browser's Intl.NumberFormat for proper localization
      formattedNumber = new Intl.NumberFormat(this.config.locale, {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
        useGrouping: true
      }).format(amount);
    } else {
      // Manual formatting with custom separators
      formattedNumber = this.formatManual(amount, precision);
    }

    if (!showSymbol) {
      return formattedNumber;
    }

    // Apply currency symbol positioning
    if (this.config.symbolPosition === 'before') {
      const space = this.config.spaceAfterSymbol ? ' ' : '';
      return `${this.config.symbol}${space}${formattedNumber}`;
    } else {
      const space = this.config.spaceAfterSymbol ? ' ' : '';
      return `${formattedNumber}${space}${this.config.symbol}`;
    }
  }

  /**
   * Format currency in compact notation (K, M, B)
   */
  formatCompact(amount: number, showSymbol: boolean = true): string {
    const absAmount = Math.abs(amount);
    const sign = amount < 0 ? '-' : '';
    
    let value: number;
    let suffix: string;
    
    if (absAmount >= 1_000_000_000) {
      value = amount / 1_000_000_000;
      suffix = 'B';
    } else if (absAmount >= 1_000_000) {
      value = amount / 1_000_000;
      suffix = 'M';
    } else if (absAmount >= 1_000) {
      value = amount / 1_000;
      suffix = 'K';
    } else {
      return this.format(amount, { showSymbol, compact: false });
    }

    // Format with 1 decimal place for compact notation
    const formatted = new Intl.NumberFormat(this.config.locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 1
    }).format(Math.abs(value));

    const numberPart = `${sign}${formatted}${suffix}`;

    if (!showSymbol) {
      return numberPart;
    }

    if (this.config.symbolPosition === 'before') {
      const space = this.config.spaceAfterSymbol ? ' ' : '';
      return `${this.config.symbol}${space}${numberPart}`;
    } else {
      const space = this.config.spaceAfterSymbol ? ' ' : '';
      return `${numberPart}${space}${this.config.symbol}`;
    }
  }

  /**
   * Manual number formatting with custom separators
   */
  private formatManual(amount: number, precision: number): string {
    const fixed = Math.abs(amount).toFixed(precision);
    const [integerPart, decimalPart] = fixed.split('.');
    
    // Add thousand separators
    const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, this.config.thousandSeparator);
    
    if (precision === 0 || !decimalPart) {
      return (amount < 0 ? '-' : '') + formattedInteger;
    }
    
    return (amount < 0 ? '-' : '') + formattedInteger + this.config.decimalSeparator + decimalPart;
  }

  /**
   * Parse a currency string back to a number
   */
  parse(currencyString: string): number | null {
    if (!currencyString || typeof currencyString !== 'string') {
      return null;
    }

    // Remove currency symbol and extra spaces
    let cleaned = currencyString.trim();
    cleaned = cleaned.replace(this.config.symbol, '');
    cleaned = cleaned.trim();

    // Handle compact notation
    const compactMatch = cleaned.match(/^(-?\d+(?:[.,]\d+)?)\s*([KMB])$/i);
    if (compactMatch) {
      const [, numberStr, suffix] = compactMatch;
      const baseNumber = this.parseNumber(numberStr);
      if (baseNumber === null) return null;

      const multipliers = { 'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000 };
      return baseNumber * multipliers[suffix.toUpperCase() as keyof typeof multipliers];
    }

    return this.parseNumber(cleaned);
  }

  /**
   * Parse a number string considering locale-specific separators
   */
  private parseNumber(numberStr: string): number | null {
    if (!numberStr) return null;

    // Normalize separators to standard format (. for thousands, . for decimal)
    let normalized = numberStr;
    
    // Handle different thousand/decimal separator combinations
    if (this.config.thousandSeparator === ' ') {
      // Space as thousand separator (Nordic countries)
      normalized = normalized.replace(/\s/g, '');
    } else if (this.config.thousandSeparator === '.') {
      // Dot as thousand separator, comma as decimal (German style)
      const parts = normalized.split(',');
      if (parts.length === 2) {
        // Has decimal part
        normalized = parts[0].replace(/\./g, '') + '.' + parts[1];
      } else {
        // No decimal part, dots are thousand separators
        normalized = normalized.replace(/\./g, '');
      }
    } else {
      // Comma as thousand separator, dot as decimal (US/UK style)
      normalized = normalized.replace(/,/g, '');
    }

    const parsed = parseFloat(normalized);
    return isNaN(parsed) ? null : parsed;
  }

  /**
   * Validate if a string is a valid currency input
   */
  isValidCurrency(input: string): boolean {
    return this.parse(input) !== null;
  }

  /**
   * Get validation message for invalid currency input
   */
  getValidationMessage(input: string): string | null {
    if (!input.trim()) {
      return 'Currency amount is required';
    }

    if (!this.isValidCurrency(input)) {
      return `Invalid currency format. Expected format: ${this.format(12345, { showSymbol: true })}`;
    }

    const parsed = this.parse(input);
    if (parsed !== null && parsed < 0) {
      return 'Currency amount cannot be negative';
    }

    return null;
  }

  /**
   * Format for input fields (typically without thousand separators for easier editing)
   */
  formatForInput(amount: number): string {
    return amount.toFixed(this.config.decimalPlaces);
  }

  /**
   * Change currency and return new formatter instance
   */
  withCurrency(currencyCode: CurrencyCode): CurrencyFormatter {
    return new CurrencyFormatter(currencyCode);
  }

  /**
   * Get currency configuration
   */
  getConfig(): CurrencyConfig {
    return { ...this.config };
  }

  /**
   * Get formatted currency symbol with proper spacing
   */
  getSymbolWithSpacing(): string {
    return this.config.symbolPosition === 'before' 
      ? this.config.symbol + (this.config.spaceAfterSymbol ? ' ' : '')
      : (this.config.spaceAfterSymbol ? ' ' : '') + this.config.symbol;
  }
}

// Default formatter instances for common use cases
export const DefaultCurrencyFormatter = new CurrencyFormatter('EUR');
export const USDFormatter = new CurrencyFormatter('USD');
export const NOKFormatter = new CurrencyFormatter('NOK');
export const SEKFormatter = new CurrencyFormatter('SEK');
export const GBPFormatter = new CurrencyFormatter('GBP');

// Utility functions for quick formatting
export function formatCurrency(
  amount: number, 
  currency: CurrencyCode = 'EUR', 
  options?: Parameters<CurrencyFormatter['format']>[1]
): string {
  const formatter = new CurrencyFormatter(currency);
  return formatter.format(amount, options);
}

export function parseCurrency(
  currencyString: string, 
  currency: CurrencyCode = 'EUR'
): number | null {
  const formatter = new CurrencyFormatter(currency);
  return formatter.parse(currencyString);
}

export function validateCurrency(
  input: string, 
  currency: CurrencyCode = 'EUR'
): string | null {
  const formatter = new CurrencyFormatter(currency);
  return formatter.getValidationMessage(input);
}

// React hook for currency formatting
export function useCurrencyFormatter(currency: CurrencyCode = 'EUR') {
  return new CurrencyFormatter(currency);
}

/**
 * Currency conversion utilities (placeholder for future implementation)
 */
export interface ExchangeRate {
  from: CurrencyCode;
  to: CurrencyCode;
  rate: number;
  timestamp: Date;
}

export class CurrencyConverter {
  private rates: Map<string, ExchangeRate> = new Map();

  /**
   * Add exchange rate
   */
  addRate(rate: ExchangeRate): void {
    const key = `${rate.from}-${rate.to}`;
    this.rates.set(key, rate);
  }

  /**
   * Convert amount between currencies
   */
  convert(amount: number, from: CurrencyCode, to: CurrencyCode): number | null {
    if (from === to) return amount;

    const key = `${from}-${to}`;
    const rate = this.rates.get(key);
    
    if (rate) {
      return amount * rate.rate;
    }

    // Try reverse conversion
    const reverseKey = `${to}-${from}`;
    const reverseRate = this.rates.get(reverseKey);
    
    if (reverseRate) {
      return amount / reverseRate.rate;
    }

    return null; // No rate available
  }

  /**
   * Format converted amount
   */
  formatConverted(
    amount: number, 
    from: CurrencyCode, 
    to: CurrencyCode,
    options?: Parameters<CurrencyFormatter['format']>[1]
  ): string | null {
    const converted = this.convert(amount, from, to);
    if (converted === null) return null;

    const formatter = new CurrencyFormatter(to);
    return formatter.format(converted, options);
  }
}

export const defaultCurrencyConverter = new CurrencyConverter();