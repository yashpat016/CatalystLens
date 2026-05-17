/**
 * Time helpers for the UI layer.
 *
 * All timestamps coming from the API are ISO-8601 UTC. We render them in
 * America/New_York for US equities.
 */

const ET_FORMATTER = new Intl.DateTimeFormat('en-US', {
  timeZone: 'America/New_York',
  year: 'numeric',
  month: 'short',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});

const ET_TIME_FORMATTER = new Intl.DateTimeFormat('en-US', {
  timeZone: 'America/New_York',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});

export function formatEtDateTime(iso: string): string {
  return `${ET_FORMATTER.format(new Date(iso))} ET`;
}

export function formatEtTime(iso: string): string {
  return ET_TIME_FORMATTER.format(new Date(iso));
}

/** Seconds since the Unix epoch -- the shape Lightweight Charts wants. */
export function toUnixSeconds(iso: string): number {
  return Math.floor(new Date(iso).getTime() / 1000);
}
