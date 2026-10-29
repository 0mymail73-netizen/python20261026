"use strict";

const STORAGE_KEY = "todolist.tasks";
const FILTERS = new Set(["all", "active", "completed"]);

const addForm = document.querySelector("#add-form");
const newTaskInput = document.querySelector("#new-task");
const todoList = document.querySelector("#todo-list");
const remainingCount = document.querySelector("#remaining-count");
const clearCompletedButton = document.querySelector("#clear-completed");
const storageNotice = document.querySelector("#storage-notice");
const emptyState = document.querySelector("#empty-state");
const emptyTitle = document.querySelector("#empty-title");
const emptyDescription = document.querySelector("#empty-description");
const filterButtons = document.querySelectorAll("[data-filter]");

let tasks = [];
let currentFilter = "all";
let storageNoticeMessage = "";
let editingTaskId = null;

function isValidTask(task) {
  return (
    task !== null &&
    typeof task === "object" &&
    typeof task.id === "string" &&
    typeof task.text === "string" &&
    task.text.trim().length > 0 &&
    typeof task.completed === "boolean" &&
    (typeof task.createdAt === "number" || typeof task.createdAt === "string")
  );
}

function loadTasks() {
  let savedValue;

  try {
    savedValue = window.localStorage.getItem(STORAGE_KEY);
  } catch (error) {
    console.error("할 일 저장소를 읽을 수 없습니다.", error);
    storageNoticeMessage = "브라우저 저장소에 접근할 수 없어 변경 사항은 현재 페이지에서만 유지됩니다.";
    return [];
  }

  if (savedValue === null) {
    return [];
  }

  try {
    const parsedValue = JSON.parse(savedValue);

    if (!Array.isArray(parsedValue) || !parsedValue.every(isValidTask)) {
      throw new TypeError("저장된 할 일 데이터의 형식이 올바르지 않습니다.");
    }

    return parsedValue;
  } catch (error) {
    console.error("저장된 할 일 데이터를 불러오지 못했습니다.", error);
    storageNoticeMessage = "저장된 목록을 읽지 못했습니다. 새 할 일을 저장하면 새 목록으로 대체됩니다.";
    return [];
  }
}

function saveTasks() {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    storageNoticeMessage = "";
    return true;
  } catch (error) {
    console.error("할 일 목록을 저장하지 못했습니다.", error);
    storageNoticeMessage = "목록 변경은 반영되었지만 브라우저에 저장하지 못했습니다. 저장 공간이나 브라우저 설정을 확인해 주세요.";
    return false;
  }
}

function getVisibleTasks() {
  if (currentFilter === "active") {
    return tasks.filter((task) => !task.completed);
  }

  if (currentFilter === "completed") {
    return tasks.filter((task) => task.completed);
  }

  return tasks;
}

function createIconButton(label, symbol, className, taskId) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `icon-button ${className}`;
  button.setAttribute("aria-label", label);
  button.dataset.action = className === "delete-button" ? "delete" : "edit";
  button.dataset.taskId = taskId;
  button.textContent = symbol;
  return button;
}

function createEditForm(task) {
  const form = document.createElement("form");
  form.className = "edit-form";
  form.dataset.taskId = task.id;

  const input = document.createElement("input");
  input.className = "edit-input";
  input.type = "text";
  input.value = task.text;
  input.setAttribute("aria-label", "할 일 내용 수정");
  input.required = true;

  const actions = document.createElement("div");
  actions.className = "edit-actions";

  const saveButton = document.createElement("button");
  saveButton.className = "small-button save-button";
  saveButton.type = "submit";
  saveButton.textContent = "저장";

  const cancelButton = document.createElement("button");
  cancelButton.className = "small-button";
  cancelButton.type = "button";
  cancelButton.dataset.action = "cancel-edit";
  cancelButton.textContent = "취소";

  actions.append(saveButton, cancelButton);
  form.append(input, actions);
  return form;
}

function createTaskElement(task) {
  const item = document.createElement("li");
  item.className = `todo-item${task.completed ? " is-completed" : ""}`;
  item.dataset.taskId = task.id;

  if (editingTaskId === task.id) {
    item.append(createEditForm(task));
    return item;
  }

  const checkbox = document.createElement("input");
  checkbox.className = "todo-checkbox";
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.dataset.action = "toggle";
  checkbox.dataset.taskId = task.id;
  checkbox.setAttribute("aria-label", `${task.text} 완료`);

  const text = document.createElement("span");
  text.className = "todo-text";
  text.textContent = task.text;

  const actions = document.createElement("div");
  actions.className = "item-actions";
  actions.append(
    createIconButton(`${task.text} 수정`, "✎", "edit-button", task.id),
    createIconButton(`${task.text} 삭제`, "×", "delete-button", task.id)
  );

  item.append(checkbox, text, actions);
  return item;
}

function updateEmptyState(visibleTasks) {
  const isEmpty = visibleTasks.length === 0;
  emptyState.hidden = !isEmpty;

  if (tasks.length === 0) {
    emptyTitle.textContent = "아직 할 일이 없어요";
    emptyDescription.textContent = "위 입력창에 오늘 할 일을 추가해 보세요.";
  } else if (currentFilter === "active") {
    emptyTitle.textContent = "진행 중인 할 일이 없어요";
    emptyDescription.textContent = "모든 할 일을 마쳤거나 아직 등록하지 않았어요.";
  } else if (currentFilter === "completed") {
    emptyTitle.textContent = "완료한 할 일이 없어요";
    emptyDescription.textContent = "할 일을 완료하면 여기에 표시돼요.";
  }
}

function render() {
  const visibleTasks = getVisibleTasks();
  const activeCount = tasks.filter((task) => !task.completed).length;

  todoList.replaceChildren(...visibleTasks.map(createTaskElement));
  remainingCount.textContent = activeCount === 0
    ? "남은 할 일이 없습니다"
    : `남은 할 일 ${activeCount}개`;
  clearCompletedButton.disabled = !tasks.some((task) => task.completed);
  storageNotice.textContent = storageNoticeMessage;
  storageNotice.hidden = storageNoticeMessage.length === 0;

  filterButtons.forEach((button) => {
    const isActive = button.dataset.filter === currentFilter;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });

  updateEmptyState(visibleTasks);

  if (editingTaskId !== null) {
    const editInput = todoList.querySelector(".edit-input");
    if (editInput) {
      editInput.focus();
      editInput.setSelectionRange(editInput.value.length, editInput.value.length);
    }
  }
}

function createTaskId() {
  if (typeof window.crypto?.randomUUID === "function") {
    return window.crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function findTask(taskId) {
  return tasks.find((task) => task.id === taskId);
}

function handleAddTask(event) {
  event.preventDefault();
  const text = newTaskInput.value.trim();

  if (text.length === 0) {
    newTaskInput.setCustomValidity("할 일 내용을 입력해 주세요.");
    newTaskInput.reportValidity();
    return;
  }

  tasks.push({
    id: createTaskId(),
    text,
    completed: false,
    createdAt: Date.now()
  });

  currentFilter = "all";
  newTaskInput.value = "";
  newTaskInput.setCustomValidity("");
  saveTasks();
  render();
  newTaskInput.focus();
}

function handleListChange(event) {
  const checkbox = event.target.closest('[data-action="toggle"]');
  if (!checkbox) {
    return;
  }

  const task = findTask(checkbox.dataset.taskId);
  if (!task) {
    return;
  }

  task.completed = checkbox.checked;
  saveTasks();
  render();
}

function handleListClick(event) {
  const actionButton = event.target.closest("[data-action]");
  if (!actionButton) {
    return;
  }

  const taskId = actionButton.dataset.taskId;

  if (actionButton.dataset.action === "edit") {
    editingTaskId = taskId;
    render();
    return;
  }

  if (actionButton.dataset.action === "cancel-edit") {
    editingTaskId = null;
    render();
    return;
  }

  if (actionButton.dataset.action === "delete") {
    tasks = tasks.filter((task) => task.id !== taskId);
    if (editingTaskId === taskId) {
      editingTaskId = null;
    }
    saveTasks();
    render();
  }
}

function handleEditSubmit(event) {
  const form = event.target.closest(".edit-form");
  if (!form) {
    return;
  }

  event.preventDefault();
  const task = findTask(form.dataset.taskId);
  const input = form.querySelector(".edit-input");
  const text = input.value.trim();

  if (!task) {
    editingTaskId = null;
    render();
    return;
  }

  if (text.length === 0) {
    input.setCustomValidity("할 일 내용을 입력해 주세요.");
    input.reportValidity();
    return;
  }

  task.text = text;
  editingTaskId = null;
  saveTasks();
  render();
}

function handleListKeydown(event) {
  if (event.key !== "Escape" || !event.target.closest(".edit-form")) {
    return;
  }

  editingTaskId = null;
  render();
}

addForm.addEventListener("submit", handleAddTask);
newTaskInput.addEventListener("input", () => newTaskInput.setCustomValidity(""));
todoList.addEventListener("change", handleListChange);
todoList.addEventListener("click", handleListClick);
todoList.addEventListener("submit", handleEditSubmit);
todoList.addEventListener("keydown", handleListKeydown);

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const selectedFilter = button.dataset.filter;
    if (FILTERS.has(selectedFilter)) {
      currentFilter = selectedFilter;
      editingTaskId = null;
      render();
    }
  });
});

clearCompletedButton.addEventListener("click", () => {
  tasks = tasks.filter((task) => !task.completed);
  editingTaskId = null;
  saveTasks();
  render();
});

tasks = loadTasks();
render();
