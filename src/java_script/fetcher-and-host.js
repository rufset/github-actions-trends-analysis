import { Octokit } from "octokit";
import env from "dotenv";
import fs, { lstatSync } from "fs";
import * as path from "path";
import result from "./results2.json" assert { type: "json" };
import yaml from "yaml";
import Yaml from "js-yaml";
import { exec, execSync } from "child_process";
import { assert, count, dir } from "console";
import git from "isomorphic-git";
import http from "isomorphic-git/http/node/index.cjs";
import Fs from "@supercharge/fs";
import nonClonedJson from "./nonClonedRepos.json" assert { type: "json" };
import remaningReposJson from "./RemainingRepos.json" assert { type: "json" };
env.config();

// Enviroment Variables
const pathToDir = process.env.PATH_TO_DIR;

// Global Variables
const dirNames = [];
const actions = [];
const gitHubActions = [];
const langDetails = {};
// const stars = {};
// const starsInAsending = [];
let counter = 0;

const myExec = async function (command) {
  try {
    execSync(command, (error, stdout, stderr) => {
      if (error) {
        console.log("error: " + error);
        return;
      }
      if (stderr) {
        console.log("stderr: " + stderr);
        return;
      }
      console.log("Success!! " + stdout);
    });
  } catch (err) {
    console.log(err);
  }
};

const writeDataToJson = function (filePath, arrayOfData) {
  fs.writeFileSync(filePath, JSON.stringify(arrayOfData), "utf8");
};

const cleanProjects = function (pathDir) {
  const dir = fs.opendirSync(pathDir);
  let pathToFolder;
  let repoFolders;
  let entryToRepo;
  while ((pathToFolder = dir.readSync()) !== null) {
    if (fs.lstatSync(pathToFolder.path).isDirectory()) {
      repoFolders = path.join(pathDir, pathToFolder.name);
      fs.readdirSync(repoFolders).forEach((entry) => {
        entryToRepo = path.join(repoFolders, entry);
        if (fs.lstatSync(entryToRepo).isDirectory() && entry !== ".github") {
          fs.rmdirSync(entryToRepo, { recursive: true, force: true });
        } else if (fs.lstatSync(entryToRepo).isFile()) {
          fs.unlinkSync(entryToRepo);
        }
      });
    }
  }
  dir.closeSync();
};

const cloneProjects = async function () {
  try {
    if (fs.existsSync(pathToDir)) {
      console.log(`The file or directory at '${pathToDir}' exists.`);
      return;
    } else {
      console.log(`The file or directory at '${pathToDir}' does not exist.`);
      //myExec("rm -rf projects && mkdir projects");
      remaningReposJson.forEach((item) => {
        myExec(
          `cd projects && git clone --depth 1 https://github.com/${item.name}`
        );
        cleanProjects(pathToDir);
      });
    }
  } catch (err) {
    console.log(err);
  }
};
cloneProjects();

// Populate tbe langDetails obj to be used to calc the adoption rate per language
const adotionRatePerLanguage = function () {
  result.items.forEach((item) => {
    if (!langDetails[item.mainLanguage]) {
      langDetails[item.mainLanguage] = {
        TotalRepo: 0,
        adopted: 0,
        names: [],
      };
    }
    langDetails[item.mainLanguage].TotalRepo++;
    langDetails[item.mainLanguage].names.push(item.name.split("/")[1]);
  });
};
adotionRatePerLanguage();

const downloadActions = function () {
  const dir = fs.opendirSync(pathToDir);
  let projectsFolder;
  let workflowsFolder;

  while ((projectsFolder = dir.readSync()) !== null) {
    dirNames.push(projectsFolder.name);
    workflowsFolder = `${pathToDir}/${projectsFolder.name}/.github/workflows`;

    if (fs.existsSync(workflowsFolder)) {
      Object.keys(langDetails).forEach((key) => {
        langDetails[key].names.forEach((repoName) => {
          if (repoName === projectsFolder.name) {
            langDetails[key].adopted++;
          }
        });
      });

      counter++;
      getActions(workflowsFolder);
    } else {
      //console.log(projectsFolder.name + " Do Not Have GitHub Actions");
    }
  }
  dir.closeSync();
};

let yamlCount = 0;
const getActions = function (pathToFileOrDir) {
  let secoundLastDir = "";
  const readYAMLFilesRecursively = (currentPath) => {
    fs.readdirSync(currentPath, { withFileTypes: true }).forEach((entry) => {
      const fullPath = path.join(currentPath, entry.name);

      if (entry.isDirectory()) {
        secoundLastDir += entry.name + "/";
        // Recursively read files in subdirectory
        readYAMLFilesRecursively(fullPath);
      } else if (
        entry.isFile() &&
        (entry.name.endsWith(".yml") || entry.name.endsWith(".yaml"))
      ) {
        // Read and process YAML file
        const content = fs.readFileSync(fullPath, "utf8");
        actions.push(secoundLastDir + entry.name);
        gitHubActions.push(content);
        yamlCount++;
      }
    });
  };
  readYAMLFilesRecursively(pathToFileOrDir);
};

downloadActions();
console.log("COUNTER:", counter);
//--------------------------------------------------------------------------

const checkEmptyFolder = async function () {
  const dir = Fs.opendirSync(pathToDir);
  let dirent;
  let emp = 0;
  let rep = 0;
  let isEmpty;
  while ((dirent = dir.readSync()) !== null) {
    rep++;
    isEmpty = await Fs.isEmptyDir(path.join(dirent.path, dirent.name));
    if (isEmpty) {
      fs.rmdirSync(path.join(dirent.path, dirent.name), {
        recursive: true,
        force: true,
      });
    }
    emp++;
  }
  console.log("non-empty: ", emp);
  console.log("All repos: ", rep);
  dir.closeSync();
};
//checkEmptyFolder();


// array of names
// want to iterate throug each name and put in an object
// loop through the obj keys and put togather ever obj that matches the most popular objects if it includes some of it if its popular names.
// present the results

// We have an array of yaml file we want to take the most popular categories among those files
// We want increse by one for each occurense of those cats
const pureActions = actions.map((action) => action.replace(/.yaml|.yml/g, ""));

const popularCategories = [
  "ci",
  "release",
  "build",
  "test",
  "codeql",
  "stale",
  "main",
  "lint",
  "publish",
  "docs",
  "deploy",
  "docs",
  "label",
  "backport",
];

function getActionsOcurrance() {
  const counts = {};

  // intilize the counts object for every cat in popularcats array
  popularCategories.forEach((category) => {
    counts[category] = { sumOfCategoryType: 0, precentageOfOccurence: 0 };
  });

  // Increment the counts obj by one for every action the include one or more cats of the popular cats array
  const updateCounts = (word) => {
    const toLower = word.toLowerCase();
    const categories = popularCategories.filter((c) => toLower.includes(c));
    if (categories.length > 0) {
      categories.forEach((category) => {
        counts[category].sumOfCategoryType++;
        counts[category].precentageOfOccurence = (
          (counts[category].sumOfCategoryType / pureActions.length) *
          100
        ).toFixed(2);
      });
    } else {
    }
  };

  // count the most popular cats by passing the actions to the updateCounts method
  pureActions.forEach((word) => updateCounts(word));

  // Sort the counts obj in decendent order to show the most popular categories
  const countsArray = Object.entries(counts);
  countsArray.sort((a, b) => b[1].sumOfCategoryType - a[1].sumOfCategoryType);
  const sortedCounts = Object.fromEntries(countsArray);

  console.log(sortedCounts);
}
getActionsOcurrance();

console.log("pureAction:", pureActions.length);

const repoContributer = {};
let contributerInAscending = [];

function contributerAffect() {
  result.items.forEach((item) => {
    const repoName = item.name.split("/")[1];
    if (!repoContributer[repoName]) {
      repoContributer[repoName] = {
        contributerSize: 0,
        name: "",
        adoptedGA: false,
      };
    }
    repoContributer[repoName].contributerSize = item.contributors;
    repoContributer[repoName].name = item.name.split("/")[1];
  });
}
contributerAffect();
contributerInAscending = Object.values(repoContributer);
contributerInAscending.sort((a, b) => a.contributors - b.contributors);
//console.log("contri:", contributerInAscending);

const allSteps = [];

const jobDetails = [];
const jobSet = new Set();
const jobInsideWorkflows = [];
function getActionJobs() {
  const dir = fs.opendirSync(pathToDir);
  let projectsFolder;
  while ((projectsFolder = dir.readSync()) !== null) {
    let path = `${pathToDir}/${projectsFolder.name}/.github/workflows`;
    if (fs.existsSync(path)) {
      fs.readdirSync(path).forEach((dir) => {
        let filePath = `${path}/${dir}`;
        try {
          const data = Yaml.load(fs.readFileSync(filePath, "utf8"));
          //console.log(Object.keys(data.jobs));
          jobInsideWorkflows.push(Object.keys(data.jobs));
          jobSet.add(data.jobs);
          jobDetails.push(data.jobs);
        } catch (err) {
          //console.error(err);
        }
      });
    }
  }
}
getActionJobs();
const runsOnArray = [];
const runsOnSet = new Set();
const modifiedActions = [];
const actionsSet = new Set();
const steps = [];
const stepsInsideJobs = [];
let totalJobs = 0;
const getJobsSteps = function () {
  jobDetails.forEach((job) => {
    totalJobs++;
    const keys = Object.keys(job ?? {});
    keys.forEach((key) => {
      steps.push(job[key].steps);
      runsOnArray.push(job[key]["runs-on"]);
      runsOnSet.add(job[key]["runs-on"]);
    });
  });
  const arr = steps;
  const arr2 = runsOnArray;
  arr2.flat(Infinity).forEach((run) => {
    runsOnSet.add(run);
  });
  arr.flat(Infinity).forEach((indx) => {
    allSteps.push(indx);
    if (indx?.uses) {
      modifiedActions.push(indx.uses);
      actionsSet.add(indx.uses);
    }
  });
};
getJobsSteps();
const stringfyArray = [];
runsOnArray.forEach((indx) => {
  if (typeof indx != "string") {
    const newindx = `${indx}`;
    stringfyArray.push(newindx);
    //console.log(newindx)
  } else {
    stringfyArray.push(indx);
  }
});

console.log("runsOn: " + stringfyArray.length);
// console.log("steps:",steps.length)
// console.log("allSteps:", allSteps.length)

const marketPlaceActions = modifiedActions.map((action) => {
  const index = action.indexOf("@");
  return index !== -1 ? action.substring(0, index) : action;
});

const lengthOfActions = marketPlaceActions.length;
//console.log("length of the steps " + steps.length)
const marketPlaceActionObj = {};
const mostCommonMarketPlaceActions = function () {
  for (const action of marketPlaceActions) {
    marketPlaceActionObj[action] = marketPlaceActionObj[action]
      ? marketPlaceActionObj[action] + 1
      : 1;
  }
  const sortedMarketPlaceActionObj = Object.entries(marketPlaceActionObj).sort(
    (a, b) => b[1] - a[1]
  );
  const newObject = Object.fromEntries(sortedMarketPlaceActionObj.slice(0, 10));
  Object.keys(newObject).forEach((key) => {
    newObject[key] =
      ((newObject[key] / lengthOfActions) * 100).toFixed(2) + "%";
  });
  console.log(newObject);
};
mostCommonMarketPlaceActions();

let selfHostCount = 0;
let ubuntuCount = 0;
let windowsCount = 0;
let macOSCount = 0;
let matrixCount = 0;
const runOnObj = {};

const runsOn = function () {
  stringfyArray.forEach((runsOn) => {
    if (runsOn.includes("matrix") && !runsOn.includes("self-hosted")) {
      matrixCount++;
    } else if (runsOn.includes("ubuntu") && !runsOn.includes("self-hosted")) {
      ubuntuCount++;
    } else if (runsOn.includes("windows") && !runsOn.includes("self-hosted")) {
      windowsCount++;
    } else if (runsOn.includes("macOS") && !runsOn.includes("self-hosted")) {
      macOSCount++;
    } else {
      selfHostCount++;
    }
  });

  runOnObj["self-host"] = selfHostCount;
  runOnObj["ubuntu"] = ubuntuCount;
  runOnObj["windows"] = windowsCount;
  runOnObj["macOS"] = macOSCount;
  runOnObj["matrix"] = matrixCount;

  const sortedRunOnArray = Object.entries(runOnObj).sort((a, b) => b[1] - a[1]);
  const newObject = Object.fromEntries(sortedRunOnArray.slice(0, 10));
  const lengthOfActions = stringfyArray.length;

  Object.keys(newObject).forEach((key) => {
    newObject[key] =
      ((newObject[key] / lengthOfActions) * 100).toFixed(2) + "%";
  });

  return newObject;
};

console.log(runsOn());
