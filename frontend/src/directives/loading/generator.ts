export const generateGUID = (): string => {
  const ran = () =>
    (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
  return `${ran() + ran()}-${ran()}-${ran()}-${ran()}-${ran()}${ran()}${ran()}`.toUpperCase();
};
