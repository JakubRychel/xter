export const timeAgo = (isoDate) => {
  const now = new Date();
  const then = new Date(isoDate);
  const seconds = Math.floor((now - then) / 1000);

  const intervals = {
    year: 365 * 24 * 3600,
    month: 30 * 24 * 3600,
    day: 24 * 3600,
    hour: 3600,
    minute: 60,
    second: 1
  };

  const formatUnit = (count, unit) => {
    const forms = {
      year: ['rok', 'lata', 'lat'],
      month: ['miesiąc', 'miesiące', 'miesięcy'],
      day: ['dzień', 'dni', 'dni'],
      hour: ['godzinę', 'godziny', 'godzin'],
      minute: ['minutę', 'minuty', 'minut']
    };

    const mod10 = count % 10;
    const mod100 = count % 100;

    const form = forms[unit];
    if (count === 1) return form[0];
    if (mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14)) return form[1];
    return form[2];
  };

  for (const [unit, value] of Object.entries(intervals)) {
    const count = Math.floor(seconds / value);

    if (count >= 1) {
      if (unit === 'second') return 'przed chwilą';
      return `${count} ${formatUnit(count, unit)} temu`;
    }
  }
}