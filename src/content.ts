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
 * Scroll animations: rendered frames live in public/sequences/<name>/, one
 * folder per width (1280 and 720), named 001.webp, 002.webp and so on.
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

/** A rendered animation that plays as the reader scrolls. */
export interface Sequence {
  /** Anchor for the section, used in the page address and the page index. */
  id: string;
  /** Folder in public/ that holds the 1280 and 720 frame folders. Ends with a slash. */
  src: string;
  frames: number;
  /** Lettered in copper traces as the section heading, and used for its link in the page index. */
  heading: string;
  intro: string;
  /** Describes the finished last frame, which is what readers without animation see. */
  alt: string;
  note: string;
  /** How long the animation lasts, as a share of the screen height. 250 when not set. */
  scroll?: number;
  /**
   * What happens over the scroll, with the stretch of it each step takes, from 0 to 1.
   * These must match the schedule the frames were rendered with.
   */
  steps: { label: string; detail: string; from: number; to: number }[];
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
  /** Rendered scroll animations, each shown as its own section after Approach. */
  sequences?: Sequence[];
}

/* ------------------------------------------------------------------ */
/*  Site                                                               */
/* ------------------------------------------------------------------ */

export const site = {
  name: 'Foster Beard',
  title: 'Foster Beard | Electrical and Computer Engineering Student',
  description:
    'Foster Beard is an electrical and computer engineering student at Western University, building hardware, robotics and AI systems. Graduating in April 2027 and open to full-time roles from Spring 2027.',
  location: 'Bobcaygeon and London, Ontario',
  /** Printed on the circuit board in the hero. */
  boardMark: 'FB-2027  REV A',
};

/** In the same order as the sections on the home page. */
export const nav: LinkItem[] = [
  { label: 'About', href: '/#about' },
  { label: 'Work', href: '/#work' },
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
  lead: 'Electrical and computer engineering student building hardware, robotics and AI systems.',
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
    { label: 'Looking for', value: 'Full-time engineering roles from Spring 2027, in the GTA or near Bobcaygeon' },
    { label: 'Based in', value: 'Bobcaygeon, ON, and London, ON for school' },
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
  intro: 'Six boards, newest first. Each one opens onto the full story.',
  cta: 'Read the case study',
};

export const projects: Project[] = [
  {
    slug: 'tethered-drone',
    name: 'Tethered window-washing drone',
    traceName: ['TETHERED', 'DRONE'],
    board: 'black',
    chip: 'ESP32',
    summary: 'A tethered quadcopter that washes high-rise windows. Power and water come up from the ground, so it carries no battery and stays up as long as the job takes.',
    role: 'Flight controller and controls lead',
    team: 'Team of 4, ECE capstone design project',
    when: 'Sept 2026 to present',
    where: 'Western University, London, ON',
    status: 'In design, demo March 2027',
    tags: ['Flight control', 'Neural-network control', 'Custom PCB', 'ESP32', 'Power over Ethernet'],
    problem: [
      'High-rise windows are cleaned by crews on ropes or in gondolas. We want a safer, cheaper way to do it: a drone that stays at the glass for as long as the job takes.',
      'That rules out a battery. Power and water both come up a tether from the ground, and an industry partner, Blondie’s Window Services, sets the requirements.',
    ],
    approach: [
      'A base station on the ground plugs into 240 V AC and converts it to about 400 V DC, which runs up the tether. A separate low-voltage Power-over-Ethernet line powers the flight controller and camera and carries their data and video. A pump sends water up a hose alongside the tether, and everything is fused.',
      'On the drone, a single step-down converter brings the high-voltage feed down to about 50 V for the motors. The drone holds a set distance from the glass while it sprays, and streams video to an operator who can send it commands. The full-size target is about 10 storeys on roughly 35 m of tether, with a 2:1 thrust-to-weight ratio.',
      'I lead the control system, which runs on our own ESP32 flight controller PCB. It is hierarchical: PID loops handle low-level stabilization, and a neural network decides where the drone should be. It holds a fixed distance from the window with ultrasonic sensing, holds height and position with GPS and a barometer, and compensates for wind and for the hose’s changing mass and reaction force as the pump turns on and off.',
      'The network is trained in a simulator, then transferred to the real drone. We will also test a second approach, one network that controls everything end to end. If the network is too heavy for the ESP32, a Raspberry Pi in the base station runs it and sends commands up the Ethernet line.',
      'I also designed the flight controller PCB and the PoE low-voltage supply. The main high-voltage power system is a teammate’s.',
      'For the demo we are building a scaled-down quad that runs on 120 V straight from the wall, with the step-down converter on board. Carbon fibre tubes pass through its 3D-printed body to form the four arms, with the wiring inside them. The body holds the flight controller, camera and converter, and the hose hangs underneath.',
    ],
    hardware: [
      { area: 'Airframe', item: 'Quadcopter; the prototype has a 3D-printed body with carbon fibre tube arms' },
      { area: 'Flight control', item: 'Custom ESP32 flight controller PCB, designed in Altium' },
      { area: 'Sensing', item: 'Ultrasonic range to the glass, GPS, barometer and a video camera' },
      { area: 'Tether power', item: '240 V AC to about 400 V DC at the base, stepped down to about 50 V on board' },
      { area: 'Low voltage and data', item: 'Power over Ethernet to the flight controller and camera' },
      { area: 'Water', item: 'Ground pump and a hose alongside the tether, to a spray nozzle' },
    ],
    software: [
      { area: 'Control', item: 'PID stabilization under a neural network that sets the position' },
      { area: 'Training', item: 'PyTorch, trained in a simulator and transferred to the real drone' },
      { area: 'Firmware', item: 'C++ on the ESP32' },
      { area: 'Modelling', item: 'MATLAB for control design and force modelling, Simscape for the step-down converter' },
      { area: 'CAD', item: 'SolidWorks' },
    ],
    results: [
      'In design, with requirements set by Blondie’s Window Services.',
      'The prototype is due to be assembled by January 2027 for testing, ahead of a live demo at Design Day in late March 2027.',
    ],
    // TODO: add real numbers as the build progresses, such as flight time, thrust margin or hold accuracy.
    metrics: [],
    diagram: {
      nodes: [
        { id: 'mains', label: '240 V AC mains', col: 0, row: 0 },
        { id: 'base', label: 'Base station', col: 1, row: 0 },
        { id: 'tether', label: '400 V DC tether', col: 2, row: 0 },
        { id: 'buck', label: 'Step-down to 50 V', col: 3, row: 0 },
        { id: 'motors', label: 'Four motors', col: 4, row: 0 },
        { id: 'poe', label: 'Power over Ethernet', col: 2, row: 1 },
        { id: 'fc', label: 'ESP32 flight controller', col: 3, row: 1 },
        { id: 'sensors', label: 'Ultrasonic, GPS, barometer', col: 4, row: 1 },
        { id: 'pump', label: 'Pump and hose', col: 2, row: 2 },
        { id: 'nozzle', label: 'Spray nozzle', col: 3, row: 2 },
      ],
      edges: [['mains', 'base'], ['base', 'tether'], ['tether', 'buck'], ['buck', 'motors'], ['base', 'poe'], ['poe', 'fc'], ['fc', 'motors'], ['sensors', 'fc'], ['base', 'pump'], ['pump', 'nozzle']],
    },
    media: [
      {
        type: 'image',
        src: 'projects/tethered-drone/render.jpg',
        alt: 'Render of the gold quadcopter beside a glass office tower, spraying a fan of water at a dirty window and leaving a clean stripe behind it, with its tether and hose running down to the ground',
        caption: 'Concept render of the full-size drone at work',
        ratio: '16/9',
      },
      { type: 'image', src: '', alt: 'The ESP32 flight controller PCB', caption: 'Flight controller PCB', ratio: '3/2' },
      { type: 'video', src: '', poster: '', alt: 'Tethered flight test', caption: 'Tethered flight test', ratio: '16/9' },
    ],
    // Rendered in Blender from Projects/TetheredDrone/Blender/tethered-drone.blend, built by td_quad.py.
    // Step timings match drone_pose() in td_anim.py for the washing scene, and EXPLODE in td_quad.py for the prototype.
    sequences: [
      {
        id: 'on-the-glass',
        src: '/sequences/tethered-drone-wash/',
        frames: 120,
        scroll: 320,
        heading: 'ON THE GLASS',
        intro: 'The full-size drone at work, about ten storeys up. It climbs on its tether, holds a set distance from the glass and sprays it, with the water pumped up from the ground. Scroll to clean the glass.',
        alt: 'Render of the gold quadcopter beside a glass office tower, spraying a window and leaving a clean, wet stripe behind it',
        note: 'Concept render made in Blender. The full-size airframe is still being designed, so its shape and sizes are illustrative.',
        steps: [
          { label: 'Climb', detail: 'On the tether, no battery', from: 0.02, to: 0.24 },
          { label: 'Hold distance', detail: 'Ultrasonic range to the glass', from: 0.24, to: 0.34 },
          { label: 'Spray', detail: 'Water from the ground', from: 0.34, to: 0.42 },
          { label: 'Sweep', detail: 'Across the pane', from: 0.42, to: 0.94 },
        ],
      },
      {
        id: 'prototype',
        src: '/sequences/tethered-drone-design/',
        frames: 132,
        scroll: 380,
        heading: 'PROTOTYPE',
        intro: 'The scaled-down demo build, taken apart. Scroll to lift off the props and motors and slide the carbon tubes out of the printed body, then open it up to the flight controller, ESCs, PoE supply and sensors, and the step-down converter, tether and nozzle beneath them.',
        alt: 'Exploded render of the prototype quadcopter: props and motors above the four carbon fibre arm tubes, and the gold printed body with its lid, flight controller, ESC board and sensors lifted out above it and the tether hub, nozzle and legs below',
        note: 'Concept render made in Blender. The prototype is still being designed, so its parts and sizes are illustrative.',
        steps: [
          { label: 'Propulsion', detail: 'Four motors and props', from: 0.04, to: 0.21 },
          { label: 'Frame', detail: 'Carbon tubes through a printed body', from: 0.24, to: 0.37 },
          { label: 'Electronics', detail: 'Flight controller, PoE supply, sensors', from: 0.4, to: 0.66 },
          { label: 'Power and water', detail: 'Step-down converter, tether, nozzle', from: 0.68, to: 0.82 },
        ],
      },
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
    when: 'July 2026 to present',
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
    slug: 'spot-welder',
    name: 'Resistance spot welder power supply',
    traceName: ['SPOT', 'WELDER'],
    board: 'red',
    chip: 'ESP32',
    summary: 'A high-current power supply on a custom PCB, with ESP32-based closed-loop current control.',
    role: 'Design and build',
    team: 'Team of 3',
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
    role: 'Design and build',
    team: 'Team of 3',
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
    // TODO: add a PCB close-up or flight footage here when you have them.
    media: [
      {
        type: 'image',
        src: 'projects/liftlabs/build-space.jpg',
        alt: 'The inflated blimp envelope with its purple fin beside a workbench, with a solar panel on the table and a 3D printer behind',
        caption: 'The envelope inflated beside the build bench, with one of the solar panels and the 3D printer',
        ratio: '16/9',
      },
      {
        type: 'image',
        src: 'projects/liftlabs/envelope.jpg',
        alt: 'The dark grey blimp envelope with purple inflatable fins, tethered indoors',
        caption: 'The 13 ft PVC envelope, inflated and tethered indoors',
        ratio: '4/3',
      },
      {
        type: 'image',
        src: 'projects/liftlabs/solar-panel.jpg',
        alt: 'A flexible monocrystalline solar panel standing against a wall',
        caption: 'One of the four 100 W flexible solar panels',
        ratio: '4/3',
      },
      {
        type: 'image',
        src: 'projects/liftlabs/motor-esc.jpg',
        alt: 'A blue brushless outrunner motor wired to an 80 A brushless ESC on a wooden table',
        caption: 'A drive motor and its 80 A brushless ESC',
        ratio: '3/2',
      },
      {
        type: 'image',
        src: 'projects/liftlabs/render.jpg',
        alt: 'Render of the finished LiftLabs blimp against a blue sky, with four solar panels across the top, purple fins and a motor arm underneath',
        caption: 'Render of the finished design',
        ratio: '16/9',
      },
    ],
    // Rendered in Blender from Projects/SolarBlimp/Blender/liftlabs-print.blend.
    // Step timings match the scene's render script: BL_render.py for the blimp, LL_render.py for the parts.
    sequences: [
      {
        id: 'design',
        src: '/sequences/liftlabs-blimp/',
        frames: 90,
        heading: 'DESIGN',
        intro: 'The finished blimp, built in Blender from photos of the envelope and the real mounting plate and motor mounts. Scroll to fly round it and watch the motors tilt.',
        alt: 'Render of the finished LiftLabs blimp: a charcoal envelope with purple inflatable fins, four flexible solar panels across the top, and 1 m arms under the belly with a tilting motor at each end',
        note: 'Rendered in Blender. The envelope, plate and motor mounts follow the real parts; the motors, props and arms are stand-ins.',
        steps: [
          { label: 'Envelope', detail: '13 ft PVC, inflatable fins', from: 0, to: 0.26 },
          { label: 'Solar array', detail: '4 × 100 W flexible panels', from: 0.26, to: 0.52 },
          { label: 'Thrust vectoring', detail: 'Motors tilt on 1 m arms', from: 0.6, to: 0.98 },
        ],
      },
      {
        id: 'parts',
        src: '/sequences/liftlabs-print/',
        frames: 72,
        heading: 'PARTS',
        intro: 'Three of the blimp’s parts from the SolidWorks model, rendered in Blender from their STL exports. Scroll to print them layer by layer.',
        alt: 'Render of the motor-to-servo mount, the mounting plate with Lift Labs cut into its face, and the GPS enclosure, all printed in purple plastic',
        note: 'Rendered in Blender. The colour and print order are for illustration.',
        steps: [
          { label: 'Motor-to-servo mount', detail: '60 × 60 × 30 mm', from: 0.05, to: 0.37 },
          { label: 'Mounting plate', detail: '305 × 181 × 20 mm', from: 0.33, to: 0.65 },
          { label: 'GPS enclosure', detail: '100 × 50 × 20 mm', from: 0.61, to: 0.93 },
        ],
      },
    ],
  },
  {
    slug: 'volume-remote',
    name: 'Motorized volume remote',
    traceName: ['VOLUME', 'REMOTE'],
    board: 'amber',
    chip: 'ESP32',
    summary: 'A wireless remote that physically turns a surround sound receiver’s volume knob.',
    role: 'Design and build',
    team: 'Solo project',
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
      {
        type: 'image',
        src: 'projects/volume-remote/render.jpg',
        alt: 'Render of the receiver with the black motor mount on its volume knob, wired to a small driver board and a grey box beside it',
        caption: 'Render of the setup',
        ratio: '16/9',
      },
    ],
    // Rendered in Blender from Projects/VolumeRemote/Blender/volume-remote.blend. Step timings match its VR_render.py.
    sequences: [
      {
        id: 'design',
        src: '/sequences/volume-remote/',
        frames: 120,
        scroll: 360,
        heading: 'DESIGN',
        intro: 'The receiver and the motor mount, modelled in Blender from a photo of the real setup. Scroll to take it apart, then watch the stepper turn the volume knob.',
        alt: 'Render of the receiver with the black motor mount over its volume knob, the display reading -20.0 dB, and wires running to a grey box beside it',
        note: 'Rendered in Blender from a photo, so sizes are estimates. The receiver is shown without its branding.',
        steps: [
          { label: 'Knob attachment', detail: 'Slides over the volume knob', from: 0.14, to: 0.3 },
          { label: 'Stepper motor', detail: 'Turns the attachment', from: 0.3, to: 0.48 },
          { label: 'ESP32', detail: 'In the box, taking the remote’s commands', from: 0.54, to: 0.72 },
          { label: 'Volume', detail: 'Turned from across the room', from: 0.84, to: 0.99 },
        ],
      },
    ],
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
      name: 'Hardware and power',
      items: ['Custom PCB design', 'Altium and Autodesk Eagle', 'SolidWorks Electrical', 'Power electronics', 'Closed-loop current control', 'Solar charge controllers', 'Three-phase power', 'SolidWorks, Fusion 360, Onshape'],
    },
    {
      name: 'Controls',
      items: ['Control systems', 'Data-driven control', 'Flight control', 'Robot kinematics', 'ROS 2', 'MATLAB, Simulink and Simscape', 'PLC ladder logic', 'Signal processing'],
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
      org: 'Copyroom',
      role: 'Co-Founder',
      dates: 'July 2026 to present',
      where: 'Ontario, Canada',
      detail: 'Co-founded and launched a two-sided marketplace for teachers, live since September 2026.',
      spans: [[2026.5, null]],
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
      org: 'Parks Canada, Trent-Severn Waterway',
      role: 'Lock and Bridge Operator',
      dates: 'June 2023 to present, seasonal',
      where: 'Gamebridge, ON',
      detail: 'Operate canal locks and swing bridge equipment over four seasons, and monitor and maintain the mechanical and electrical lock equipment.',
      // Each season ran June to September.
      spans: [[2023.42, 2023.75], [2024.42, 2024.75], [2025.42, 2025.75], [2026.42, 2026.75]],
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
      org: 'University of Guelph',
      role: 'Bee Research Technician',
      dates: 'June 2022 to June 2023',
      where: 'Bobcaygeon, ON',
      detail: 'Fabricated an alternative method for overwintering queens and colonies that improved survival rates, and collected data for a PhD research project.',
      spans: [[2022.42, 2023.42]],
    },
    {
      org: 'Kawartha Lakes Honey',
      role: 'Beekeeper',
      dates: 'Jan 2020 to June 2023',
      where: 'Bobcaygeon, ON',
      detail: 'Maintained healthy colonies, and built and repaired beekeeping equipment in the woodshop, often working independently.',
      spans: [[2020.0, 2023.42]],
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
  links: [
    { label: 'Email', value: 'foster5beard@gmail.com', href: 'mailto:foster5beard@gmail.com' },
    { label: 'LinkedIn', value: 'in/fosterbeard', href: 'https://www.linkedin.com/in/fosterbeard' },
    { label: 'GitHub', value: 'fosteb5', href: 'https://github.com/fosteb5' },
    { label: 'Phone', value: '(705) 731-9471', href: 'tel:+17057319471' },
  ],
};

export const notFound = {
  heading: 'OPEN CIRCUIT',
  body: 'This page isn’t connected to anything. The link may be out of date.',
  cta: 'Back to the board',
};
