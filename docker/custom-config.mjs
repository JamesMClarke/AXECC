
export default {
    extends: 'lighthouse:default',
    settings: {
      maxWaitForFcp: 30 * 1000,
      maxWaitForLoad: 50 * 1000,
      formFactor: 'desktop',
      onlyCategories: ['accessibility'],
      ignoreStatusCode: true,
      screenEmulation: {
        mobile: false,
        width: 1350,
        height: 940,
        deviceScaleFactor: 1,
        disabled: false,
      },
      emulatedUserAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    },
  };
