/**
 * Everything you can read on the site lives in this file.
 * Edit text, projects and links here. You should not need to touch a component.
 *
 * Search for "TODO" to find what still needs your input.
 * TODO items in `metrics` and `media` stay hidden or show a neat placeholder on
 * the live site, so the site is safe to publish while they are unfinished.
 *
 * Photos: put them in src/assets/projects/<slug>/ and set `src`, for example
 *   src: 'projects/liftlabs/first-flight.jpg'
 * The first photo in a project's `media` is also its picture on the home page.
 * A project with no photo yet shows its system diagram there instead.
 * Videos: put them in public/video/ and set `src`, for example
 *   src: '/video/liftlabs-flight.mp4'
 */

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

/** Solder mask colour for a project's board. Defined in src/lib/boards.ts. */
export type BoardColour = 'green' | 'blue' | 'black' | 'red' | 'purple' | 'amber' | 'white' | 'berry';

export interface LinkItem {
  label: string;
  href: string;
}

export interface Media {
  type: 'image' | 'video';
  /** Path to the file. Leave empty to show a placeholder until you have it. */
  src?: string;
  /** Video only: a still image shown before it plays, stored in public/. */
  poster?: string;
  /** Describe the picture for screen readers. */
  alt: string;
  caption: string;
  /** Width / height of the frame. */
  ratio?: '16/9' | '3/2' | '4/3' | '1/1';
}

export interface DiagramNode {
  id: string;
  label: string;
  /** Column, counted from the left. */
  col: number;
  /** Row, counted from the top. Halves are fine. */
  row: number;
}

export interface Diagram {
  nodes: DiagramNode[];
  /** Connections as [from id, to id]. */
  edges: [string, string][];
}

export interface StackItem {
  /** What the part does. */
  area: string;
  /** What was used. */
  item: string;
}

export interface Project {
  /** Used in the web address: /work/<slug> */
  slug: string;
  name: string;
  /** Lettered in copper traces. Capitals, one array entry per line. */
  traceName: string[];
  board: BoardColour;
  /** Text printed on the chip on this project's hero board. */
  chip: string;
  /** One sentence, shown on the home page and at the top of the case study. */
  summary: string;
  role: string;
  team?: string;
  when: string;
  where?: string;
  status?: string;
  tags: string[];
  /** Shown as buttons on the home page card and the case study. Opens in a new tab. */
  links?: LinkItem[];
  problem: string[];
  approach: string[];
  hardware?: StackItem[];
  software?: StackItem[];
  /** Results you can state today. */
  results: string[];
  /**
   * Hard numbers. Add real ones when you have them, for example
   *   { label: 'Peak weld current', value: '850 A' }
   * This section stays hidden while the list is empty.
   */
  metrics: { label: string; value: string }[];
  diagram: Diagram;
  media: Media[];
}

/* ------------------------------------------------------------------ */
/*  Site                                                               */
/* ------------------------------------------------------------------ */

export const site = {
  name: 'Foster Beard',
  title: 'Foster Beard | Electrical and Computer Engineer',
  description:
    'Foster Beard is an electrical and computer engineer building hardware, robotics and AI systems. Graduating from Western University in April 2027 and open to full-time roles from Spring 2027.',
  location: 'Ontario, Canada (GTA / London)',
  /** Printed on the circuit board in the hero. */
  boardMark: 'FB-2027  REV A',
};

export const nav: LinkItem[] = [
  { label: 'Work', href: '/#work' },
  { label: 'About', href: '/#about' },
  { label: 'Toolbox', href: '/#toolbox' },
  { label: 'Experience', href: '/#experience' },
  { label: 'Résumé', href: '/#resume' },
];

/* ------------------------------------------------------------------ */
/*  Hero                                                               */
/* ------------------------------------------------------------------ */

export const hero = {
  /** Lettered in copper traces. Capitals, one array entry per line. */
  name: ['FOSTER', 'BEARD'],
  lead: 'Electrical and computer engineer building hardware, robotics and AI systems.',
  availability: 'Graduating April 2027. Open to full-time roles from Spring 2027.',
  primaryCta: { label: 'View work', href: '/#work' },
  secondaryCta: { label: 'Get in touch', href: '/#contact' },
};

/* ------------------------------------------------------------------ */
/*  About                                                              */
/* ------------------------------------------------------------------ */

export const about = {
  heading: 'ABOUT',
  statement:
    'I’m a fifth-year Electrical and Computer Engineering student at Western University, with a dual degree in AI Systems Engineering. I take projects from concept to working hardware, from an autonomous solar-powered blimp to a tethered window-washing drone.',
  facts: [
    { label: 'Studying', value: 'BESc, Electrical & Computer Engineering and AI Systems Engineering (dual degree), Western University' },
    { label: 'Graduating', value: 'April 2027' },
    { label: 'Looking for', value: 'Full-time engineering roles starting Spring 2027' },
    { label: 'Based in', value: 'Ontario (GTA / London)' },
  ],
  // TODO: add a portrait to src/assets/projects/about/ and set src, for example 'projects/about/portrait.jpg'.
  portrait: {
    type: 'image',
    src: '',
    alt: 'Portrait of Foster Beard',
    caption: 'Portrait',
    ratio: '1/1',
  } satisfies Media,
};

/* ------------------------------------------------------------------ */
/*  Featured work                                                      */
/* ------------------------------------------------------------------ */

export const work = {
  heading: 'FEATURED WORK',
  intro: 'Seven boards, from an airship to an app. Each one opens onto the full story.',
  cta: 'Read the case study',
};

export const projects: Project[] = [
  {
    slug: 'liftlabs',
    name: 'LiftLabs',
    traceName: ['LIFTLABS'],
    board: 'blue',
    chip: 'ESP32',
    summary: 'Electrical, software and control systems for an autonomous solar-powered blimp.',
    role: 'Electrical, software and controls engineer',
    team: 'Team of 5',
    when: 'Sept 2024 to present',
    where: 'London, ON',
    tags: ['Custom PCBs', 'ESP32', 'Solar charging', 'Thrust vectoring', 'SolidWorks'],
    links: [
      { label: 'liftlabs.ca', href: 'https://liftlabs.ca' },
      { label: 'Firmware on GitHub', href: 'https://github.com/fosteb5/LiftLabs' },
    ],
    // TODO: confirm this framing of the problem. It is written from your résumé.
    problem: [
      'An autonomous airship has to live on the power it collects. Solar charging, sensing, propulsion and control all have to work together on one airframe.',
    ],
    approach: [
      'I designed custom PCBs that bring ESP32 microcontrollers, solar charge controllers, GPS, an altimeter and a gyroscope into one electrical system.',
      'I wrote the motor control firmware for a thrust-vectoring propulsion system and built aerodynamic models of the airframe.',
      'I produced the CAD and electrical schematics in SolidWorks and SolidWorks Electrical, and maintained the project’s web documentation.',
    ],
    hardware: [
      { area: 'Control', item: 'ESP32 microcontrollers on custom PCBs' },
      { area: 'Power', item: 'Solar charge controllers' },
      { area: 'Sensing', item: 'GPS, altimeter and gyroscope' },
      { area: 'Propulsion', item: 'Thrust-vectoring motors' },
    ],
    software: [
      { area: 'Firmware', item: 'Motor control firmware' },
      { area: 'Modelling', item: 'Aerodynamic models of the airframe' },
      { area: 'Design', item: 'SolidWorks and SolidWorks Electrical' },
    ],
    results: ['Applied for and secured project funding from the Thompson Engineering Fund.'],
    // TODO: add real numbers, such as flight time, altitude or solar output.
    metrics: [],
    diagram: {
      nodes: [
        { id: 'solar', label: 'Solar cells', col: 0, row: 0 },
        { id: 'charge', label: 'Charge controller', col: 1, row: 0 },
        { id: 'gps', label: 'GPS', col: 0, row: 1 },
        { id: 'alt', label: 'Altimeter', col: 0, row: 2 },
        { id: 'gyro', label: 'Gyroscope', col: 0, row: 3 },
        { id: 'esp', label: 'ESP32', col: 2, row: 1.5 },
        { id: 'motor', label: 'Motor firmware', col: 3, row: 1.5 },
        { id: 'thrust', label: 'Thrust vectoring', col: 4, row: 1.5 },
      ],
      edges: [['solar', 'charge'], ['charge', 'esp'], ['gps', 'esp'], ['alt', 'esp'], ['gyro', 'esp'], ['esp', 'motor'], ['motor', 'thrust']],
    },
    media: [
      // TODO: swap in a photo of the real blimp when you have one. This render comes from liftlabs.ca.
      {
        type: 'image',
        src: 'projects/liftlabs/blimp.jpg',
        alt: 'Concept render of the LiftLabs blimp, with a solar array along its top and a propulsion pod underneath',
        caption: 'Concept render of the blimp, from liftlabs.ca',
        ratio: '16/9',
      },
      { type: 'image', src: '', alt: 'The LiftLabs blimp in flight', caption: 'The blimp in flight', ratio: '16/9' },
      { type: 'image', src: '', alt: 'A LiftLabs custom PCB', caption: 'Custom PCB close-up', ratio: '3/2' },
      { type: 'video', src: '', poster: '', alt: 'Thrust-vectoring test', caption: 'Thrust-vectoring test', ratio: '16/9' },
    ],
  },
  {
    slug: 'tethered-drone',
    name: 'Tethered window-washing drone',
    traceName: ['TETHERED', 'DRONE'],
    board: 'black',
    chip: 'ESP32',
    summary: 'A tethered hexacopter that cleans windows up to 12 storeys, fed with power and water from the ground.',
    role: 'Flight controller and controls lead',
    team: 'Team of 4, capstone design project',
    when: 'Sept 2026 to present',
    where: 'Western University, London, ON',
    status: 'In development',
    tags: ['Flight control', 'Custom PCB', 'ESP32', 'Computer vision', 'Raspberry Pi'],
    // TODO: confirm this framing of the problem. It is written from your résumé.
    problem: [
      'A drone that carries its own water and battery spends most of its lift on the load. To clean windows up to 12 storeys, the power and the water had to come from somewhere else.',
      'We are defining the requirements with an industry partner, Blondie’s Window Services.',
    ],
    approach: [
      'The hexacopter is tethered to a generator-powered base station on the ground. The base station feeds it power and water, so the aircraft carries no battery.',
      'I lead the design of the custom ESP32-based flight controller PCB, its flight control firmware and the control system.',
      'I’m developing a computer vision model that classifies clean and dirty glass. It supports an optional Raspberry Pi autonomous mode that detects windows and obstacles.',
    ],
    hardware: [
      { area: 'Airframe', item: 'Tethered hexacopter' },
      { area: 'Flight control', item: 'Custom ESP32-based flight controller PCB' },
      { area: 'Ground support', item: 'Generator-powered base station for power and water' },
      { area: 'Autonomy', item: 'Optional Raspberry Pi mode' },
    ],
    software: [
      { area: 'Firmware', item: 'Flight control firmware and control system' },
      { area: 'Vision', item: 'Clean and dirty glass classifier, window and obstacle detection' },
    ],
    results: [
      'Requirements are being defined with Blondie’s Window Services.',
      'The flight controller, firmware and vision model are in development for the capstone project.',
    ],
    // TODO: add real numbers as the build progresses, such as flight time, thrust margin or model accuracy.
    metrics: [],
    diagram: {
      nodes: [
        { id: 'gen', label: 'Generator', col: 0, row: 0 },
        { id: 'base', label: 'Base station', col: 1, row: 0 },
        { id: 'tether', label: 'Power and water tether', col: 2, row: 0 },
        { id: 'fc', label: 'ESP32 flight controller', col: 3, row: 0 },
        { id: 'motors', label: 'Six motors', col: 4, row: 0 },
        { id: 'cv', label: 'Glass classifier', col: 2, row: 1.5 },
        { id: 'pi', label: 'Raspberry Pi', col: 3, row: 1.5 },
      ],
      edges: [['gen', 'base'], ['base', 'tether'], ['tether', 'fc'], ['fc', 'motors'], ['cv', 'pi'], ['pi', 'fc']],
    },
    media: [
      { type: 'image', src: '', alt: 'The tethered hexacopter', caption: 'The hexacopter on the bench', ratio: '16/9' },
      { type: 'image', src: '', alt: 'The ESP32 flight controller PCB', caption: 'Flight controller PCB', ratio: '3/2' },
      { type: 'video', src: '', poster: '', alt: 'Tethered flight test', caption: 'Tethered flight test', ratio: '16/9' },
    ],
  },
  {
    slug: 'spot-welder',
    name: 'Resistance spot welder power supply',
    traceName: ['SPOT', 'WELDER'],
    board: 'red',
    chip: 'ESP32',
    summary: 'A high-current power supply on a custom PCB, with ESP32-based closed-loop current control.',
    role: 'Design and build', // TODO: confirm, and add a team if this was not a solo project.
    when: 'Jan 2026 to May 2026',
    tags: ['Power electronics', 'Closed-loop control', 'ESP32', 'Custom PCB', 'Hall-effect sensing'],
    // TODO: confirm this framing of the problem. It is written from your résumé.
    problem: [
      'A resistance spot weld depends on the current driven through the joint, so the supply needs stable feedback and control at high current.',
    ],
    approach: [
      'I designed and built a high-current power supply on a custom PCB.',
      'An ESP32 runs the closed-loop current control.',
      'Hall-effect current sensing with low-pass filtering gives the loop stable feedback for weld control.',
    ],
    hardware: [
      { area: 'Power stage', item: 'High-current supply on a custom PCB' },
      { area: 'Control', item: 'ESP32' },
      { area: 'Sensing', item: 'Hall-effect current sensor with low-pass filtering' },
    ],
    software: [{ area: 'Firmware', item: 'Closed-loop current control' }],
    results: ['Taken from design to built hardware between January and May 2026.'],
    // TODO: add real numbers, such as peak current, pulse length or loop rate.
    metrics: [],
    diagram: {
      nodes: [
        { id: 'supply', label: 'High-current supply', col: 0, row: 0 },
        { id: 'weld', label: 'Weld electrodes', col: 3, row: 0 },
        { id: 'hall', label: 'Hall-effect sensor', col: 3, row: 1.5 },
        { id: 'lpf', label: 'Low-pass filter', col: 2, row: 1.5 },
        { id: 'esp', label: 'ESP32 control loop', col: 1, row: 1.5 },
      ],
      edges: [['supply', 'weld'], ['esp', 'supply'], ['lpf', 'esp'], ['hall', 'lpf'], ['weld', 'hall']],
    },
    media: [
      { type: 'image', src: '', alt: 'The spot welder power supply', caption: 'The finished supply', ratio: '16/9' },
      { type: 'image', src: '', alt: 'The custom PCB for the welder', caption: 'Custom PCB', ratio: '3/2' },
      { type: 'video', src: '', poster: '', alt: 'A test weld', caption: 'A test weld', ratio: '16/9' },
    ],
  },
  {
    slug: 'smart-home',
    name: 'Smart home system',
    traceName: ['SMART', 'HOME'],
    board: 'purple',
    chip: 'RPI 5',
    summary: 'A Raspberry Pi 5 home automation hub with integrated sensors and computer vision facial recognition.',
    role: 'Design and build', // TODO: confirm, and add a team if this was not a solo project.
    when: 'Jan 2026 to April 2026',
    tags: ['Raspberry Pi 5', 'Computer vision', 'Facial recognition', 'Sensors'],
    // TODO: confirm this framing of the problem. It is written from your résumé.
    problem: ['A home automation system needs one hub that can read its sensors and recognise who is there.'],
    approach: [
      'I built the hub on a Raspberry Pi 5 with integrated sensors.',
      'I added computer vision-based facial recognition using ML models.',
    ],
    hardware: [
      { area: 'Hub', item: 'Raspberry Pi 5' },
      { area: 'Inputs', item: 'Integrated sensors' },
    ],
    software: [{ area: 'Vision', item: 'Facial recognition using ML models' }],
    results: ['A working home automation hub built between January and April 2026.'],
    // TODO: add real numbers, such as recognition accuracy or response time.
    metrics: [],
    diagram: {
      nodes: [
        { id: 'sensors', label: 'Sensors', col: 0, row: 0 },
        { id: 'camera', label: 'Camera', col: 0, row: 1 },
        { id: 'face', label: 'Facial recognition', col: 1, row: 1 },
        { id: 'pi', label: 'Raspberry Pi 5 hub', col: 2, row: 0.5 },
        { id: 'home', label: 'Home automation', col: 3, row: 0.5 },
      ],
      edges: [['sensors', 'pi'], ['camera', 'face'], ['face', 'pi'], ['pi', 'home']],
    },
    media: [
      { type: 'image', src: '', alt: 'The Raspberry Pi 5 smart home hub', caption: 'The hub', ratio: '16/9' },
      { type: 'image', src: '', alt: 'The facial recognition view', caption: 'Facial recognition in use', ratio: '3/2' },
    ],
  },
  {
    slug: 'volume-remote',
    name: 'Motorized volume remote',
    traceName: ['VOLUME', 'REMOTE'],
    board: 'amber',
    chip: 'ESP32',
    summary: 'A wireless remote that physically turns a surround sound receiver’s volume knob.',
    role: 'Design and build', // TODO: confirm, and add a team if this was not a solo project.
    when: 'Sept 2024, redesigned Feb 2026',
    tags: ['ESP32', 'Stepper motor', 'Custom PCB', 'Low-power firmware', 'SolidWorks'],
    // TODO: confirm this framing of the problem. It is written from your résumé.
    problem: ['The goal was to change a receiver’s volume from across the room by turning its physical knob.'],
    approach: [
      'Two ESP32s link the remote to a stepper motor that turns the receiver’s volume knob.',
      'I designed a custom PCB in Autodesk Eagle with a display and low-power C++ firmware.',
      'I modelled the motor mount in SolidWorks.',
    ],
    hardware: [
      { area: 'Wireless link', item: 'Two ESP32s' },
      { area: 'Actuator', item: 'Stepper motor on a SolidWorks mount' },
      { area: 'Remote', item: 'Custom Eagle PCB with a display' },
    ],
    software: [{ area: 'Firmware', item: 'Low-power C++' }],
    results: ['First built in September 2024, then redesigned in February 2026.'],
    // TODO: add real numbers, such as battery life or wireless range.
    metrics: [],
    diagram: {
      nodes: [
        { id: 'remote', label: 'Remote and display', col: 0, row: 0 },
        { id: 'tx', label: 'ESP32', col: 1, row: 0 },
        { id: 'rx', label: 'ESP32', col: 2, row: 0 },
        { id: 'step', label: 'Stepper motor', col: 3, row: 0 },
        { id: 'knob', label: 'Volume knob', col: 4, row: 0 },
      ],
      edges: [['remote', 'tx'], ['tx', 'rx'], ['rx', 'step'], ['step', 'knob']],
    },
    media: [
      { type: 'image', src: '', alt: 'The motorized volume remote', caption: 'Remote and motor mount', ratio: '16/9' },
      { type: 'video', src: '', poster: '', alt: 'The knob turning from the remote', caption: 'The knob turning', ratio: '16/9' },
    ],
  },
  {
    slug: 'copyroom',
    name: 'Copyroom',
    traceName: ['COPYROOM'],
    board: 'white',
    chip: 'WEB',
    summary: 'A Canadian online marketplace where teachers buy and sell classroom resources.',
    role: 'Co-founder',
    when: '2025 to present',
    where: 'Ontario, Canada',
    status: 'Live since September 2026',
    tags: ['Two-sided marketplace', 'Stripe Connect', 'GST/HST', 'Playwright', 'Claude Code'],
    links: [{ label: 'copyroom.ca', href: 'https://copyroom.ca' }],
    // TODO: confirm this framing of the problem. It is written from your résumé.
    problem: [
      'Teachers make classroom resources that other teachers can use. A Canadian marketplace for them has to handle accounts, file delivery, seller payouts and sales tax properly.',
    ],
    approach: [
      'I built buyer and seller accounts, file uploads, and Stripe Connect split payments with Canadian GST/HST handling.',
      'I use AI-assisted development, with Claude Code running parallel agents and Playwright testing, for site redesigns and performance optimization.',
      'I run customer acquisition through Meta ad campaigns with AI-generated video and direct seller outreach.',
    ],
    software: [
      { area: 'Accounts', item: 'Buyer and seller accounts' },
      { area: 'Files', item: 'Resource uploads' },
      { area: 'Payments', item: 'Stripe Connect split payments with GST/HST handling' },
      { area: 'Quality', item: 'Playwright testing' },
      { area: 'Growth', item: 'Meta ad campaigns and direct seller outreach' },
    ],
    results: ['Live for Canadian teachers since September 2026.'],
    // TODO: add real numbers, such as sellers, resources listed or sales.
    metrics: [],
    diagram: {
      nodes: [
        { id: 'sellers', label: 'Sellers', col: 0, row: 0 },
        { id: 'buyers', label: 'Buyers', col: 0, row: 1 },
        { id: 'site', label: 'Copyroom', col: 1, row: 0.5 },
        { id: 'files', label: 'File uploads', col: 2, row: 0 },
        { id: 'stripe', label: 'Stripe Connect', col: 2, row: 1 },
        { id: 'tax', label: 'GST/HST', col: 3, row: 1 },
      ],
      edges: [['sellers', 'site'], ['buyers', 'site'], ['site', 'files'], ['site', 'stripe'], ['stripe', 'tax']],
    },
    media: [
      {
        type: 'image',
        src: 'projects/copyroom/storefront.jpg',
        alt: 'The Copyroom home page, with a resource search box and the headline: Classroom resources from Canadian teachers, for Canadian classrooms',
        caption: 'The Copyroom storefront, November 2026',
        ratio: '16/9',
      },
      { type: 'image', src: '', alt: 'A Copyroom seller dashboard', caption: 'Seller view', ratio: '3/2' },
    ],
  },
  {
    slug: 'watch-converter',
    name: 'Apple Watch unit converter',
    traceName: ['UNIT', 'CONVERTER'],
    board: 'berry',
    chip: 'SWIFT',
    summary: 'A unit converter app for Apple Watch, written in SwiftUI.',
    role: 'Design and build', // TODO: confirm.
    when: '2026',
    tags: ['SwiftUI', 'Xcode', 'watchOS'],
    // TODO: confirm this framing of the problem. It is written from your résumé.
    problem: ['Quick unit conversions are a natural fit for something already on your wrist.'],
    approach: ['I wrote the app in SwiftUI using Xcode.'],
    software: [
      { area: 'Interface', item: 'SwiftUI' },
      { area: 'Tooling', item: 'Xcode' },
    ],
    results: ['A working unit converter for Apple Watch.'],
    metrics: [],
    diagram: {
      nodes: [
        { id: 'in', label: 'Value and units', col: 0, row: 0 },
        { id: 'logic', label: 'Conversion', col: 1, row: 0 },
        { id: 'ui', label: 'SwiftUI view', col: 2, row: 0 },
      ],
      edges: [['in', 'logic'], ['logic', 'ui']],
    },
    media: [{ type: 'image', src: '', alt: 'The converter on an Apple Watch', caption: 'The app on the wrist', ratio: '1/1' }],
  },
];

/* ------------------------------------------------------------------ */
/*  Toolbox                                                            */
/* ------------------------------------------------------------------ */

export const toolbox = {
  heading: 'TOOLBOX',
  chipLabel: 'FOSTER BEARD',
  groups: [
    {
      name: 'Embedded',
      items: ['ESP32', 'Raspberry Pi', 'Arduino', 'Embedded C and C++', 'RTOS and real-time scheduling', 'Interrupt-driven firmware', 'Motor control', 'Sensor integration and calibration'],
    },
    {
      name: 'PCB design and power',
      items: ['Custom PCB design', 'Autodesk Eagle', 'SolidWorks Electrical', 'Power electronics', 'Closed-loop current control', 'Solar charge controllers', 'Three-phase power', 'SolidWorks, Fusion 360, Onshape'],
    },
    {
      name: 'Controls',
      items: ['Control systems', 'Data-driven control', 'Flight control', 'Robot kinematics', 'ROS 2', 'MATLAB and Simulink', 'PLC ladder logic', 'Signal processing'],
    },
    {
      name: 'Machine learning',
      items: ['PyTorch', 'TensorFlow', 'scikit-learn', 'OpenCV', 'Computer vision', 'Neural network design', 'Vertex AI and AutoML', 'Local LLMs'],
    },
    {
      name: 'Software',
      items: ['Python', 'C and C++', 'Java', 'Swift and SwiftUI', 'SQL', 'Git and GitHub', 'Stripe API', 'Claude Code'],
    },
  ],
};

/* ------------------------------------------------------------------ */
/*  Experience                                                         */
/*  Dates use decimal years. 2023.42 is about June 2023.               */
/*  Leave `end` empty for something that is still going.               */
/* ------------------------------------------------------------------ */

export const experience = {
  heading: 'EXPERIENCE',
  intro: 'Read it like a timing diagram. Each line goes high while that role was running.',
  timelineStart: 2020,
  timelineEnd: 2028,
  signals: [
    {
      org: 'Kawartha Lakes Honey',
      role: 'Beekeeper',
      dates: 'Jan 2020 to June 2023',
      where: 'Bobcaygeon, ON',
      detail: 'Maintained healthy colonies, and built and repaired beekeeping equipment in the woodshop, often working independently.',
      spans: [[2020.0, 2023.42]],
    },
    {
      org: 'University of Guelph',
      role: 'Bee Research Technician',
      dates: 'June 2022 to June 2023',
      where: 'Bobcaygeon, ON',
      detail: 'Fabricated an alternative method for overwintering queens and colonies that improved survival rates, and collected data for a PhD research project.',
      spans: [[2022.42, 2023.42]],
    },
    {
      org: 'Western University',
      role: 'BESc, Electrical & Computer Engineering and AI Systems Engineering',
      dates: 'Sept 2022 to April 2027 (expected)',
      where: 'London, ON',
      detail: 'Dual degree. Coursework includes real-time and embedded systems, robotics, power systems and data-driven control.',
      spans: [[2022.67, 2027.25]],
    },
    {
      org: 'Parks Canada, Trent-Severn Waterway',
      role: 'Lock and Bridge Operator',
      dates: 'June 2023 to present, seasonal',
      where: 'Gamebridge, ON',
      detail: 'Operate canal locks and swing bridge equipment over four seasons, and monitor and maintain the mechanical and electrical lock equipment.',
      // TODO: confirm the months each season ran.
      spans: [[2023.42, 2023.75], [2024.42, 2024.75], [2025.42, 2025.75], [2026.42, 2026.75]],
    },
    {
      org: 'LiftLabs',
      role: 'Electrical, Software and Controls Engineer',
      dates: 'Sept 2024 to present',
      where: 'London, ON',
      detail: 'Custom PCBs, motor control firmware and aerodynamic models for an autonomous solar-powered blimp.',
      spans: [[2024.67, null]],
    },
    {
      org: 'Copyroom',
      role: 'Co-Founder',
      dates: '2025 to present',
      where: 'Ontario, Canada',
      detail: 'Co-founded and launched a two-sided marketplace for teachers, live since September 2026.',
      spans: [[2025.0, null]],
    },
  ],
  next: {
    role: 'Full-time engineering role',
    dates: 'From Spring 2027',
    start: 2027.33,
  },
  recognition: [
    '2nd place, Western Engineering Competition, Senior Design: led development of a small-scale robot prototype',
    'Ivey Case Competition participant',
    'Olympic Spirit Award, Sturgeon Lake Thunder Minor Hockey Association',
    'Computer Science Award, I.E. Weldon Secondary School',
  ],
} as const;

/* ------------------------------------------------------------------ */
/*  Résumé                                                             */
/* ------------------------------------------------------------------ */

export const resume = {
  heading: 'RÉSUMÉ',
  blurb: 'The two-page version, with every project, role and tool.',
  label: 'Download résumé',
  meta: 'PDF, 2 pages',
  // Replace this file in public/resume/ whenever your résumé changes.
  href: '/resume/foster-beard-resume.pdf',
};

/* ------------------------------------------------------------------ */
/*  Contact                                                            */
/* ------------------------------------------------------------------ */

export const contact = {
  heading: 'GET IN TOUCH',
  blurb: 'I’m looking for full-time engineering roles starting Spring 2027, in hardware, robotics and AI systems.',
  location: 'Based in Ontario (GTA / London)',
  links: [
    { label: 'Email', value: 'foster5beard@gmail.com', href: 'mailto:foster5beard@gmail.com' },
    { label: 'LinkedIn', value: 'in/fosterbeard', href: 'https://www.linkedin.com/in/fosterbeard' },
    // TODO: confirm this is the GitHub profile you want to show.
    { label: 'GitHub', value: 'fosteb5', href: 'https://github.com/fosteb5' },
    { label: 'Phone', value: '(705) 731-9471', href: 'tel:+17057319471' },
  ],
};

export const notFound = {
  heading: 'OPEN CIRCUIT',
  body: 'This page isn’t connected to anything. The link may be out of date.',
  cta: 'Back to the board',
};
