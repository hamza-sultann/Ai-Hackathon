export const ROUTES = {
  HOME: '/',
  WORKSPACES: '/workspaces',
  
  ANALYST: {
    ROOT: '/analyst',
    GRID: '/analyst/grid',
    FEEDER: (feederId: string) => `/analyst/feeders/${feederId}`,
    FEEDER_PARAM: '/analyst/feeders/:feederId',
    PMT: (pmtId: string) => `/analyst/pmts/${pmtId}`,
    PMT_PARAM: '/analyst/pmts/:pmtId',
    INVESTIGATIONS: '/analyst/investigations',
    CONSUMER_INVESTIGATION: (consumerId: string) => `/analyst/investigations/${consumerId}`,
    CONSUMER_INVESTIGATION_PARAM: '/analyst/investigations/:consumerId',
    COMPARISON: '/analyst/comparison',
    JOB_CARDS: '/analyst/job-cards',
    JOB_CARD_DETAIL: (jobCardId: string) => `/analyst/job-cards/${jobCardId}`,
    JOB_CARD_DETAIL_PARAM: '/analyst/job-cards/:jobCardId',
  },

  FIELD: {
    ROOT: '/field',
    JOBS: '/field/jobs',
    JOB_DETAIL: (jobCardId: string) => `/field/jobs/${jobCardId}`,
    JOB_DETAIL_PARAM: '/field/jobs/:jobCardId',
    TEAM: '/field/team',
    HISTORY: '/field/history',
  },

  ADMIN: {
    ROOT: '/admin',
    DATA_SOURCES: '/admin/data-sources',
    MODELS: '/admin/models',
    USERS: '/admin/users',
    AUDIT: '/admin/audit',
    CONFIGURATION: '/admin/configuration',
  },
} as const;
