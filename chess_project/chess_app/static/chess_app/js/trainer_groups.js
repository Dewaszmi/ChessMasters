function createGroup() {
  const name = document.getElementById("group-name").value;

  fetch(window.AJAX_CREATE_GROUP_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  })
  .then(r => r.json())
  .then(data => {
    if (!data.id) return;

    document.querySelectorAll(".group-select").forEach(sel => {
      const opt = document.createElement("option");
      opt.value = data.id;
      opt.textContent = data.name;
      sel.appendChild(opt);
    });

    document.getElementById("group-name").value = "";
  });
}

function assignStudent(studentId, btn) {
  const select = btn.previousElementSibling;
  const groupId = select.value;
  const row = btn.closest("tr");

  fetch(window.AJAX_ASSIGN_STUDENT_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_id: studentId,
      group_id: groupId
    })
  })
  .then(() => {
    row.querySelector(".current-group").textContent =
      select.options[select.selectedIndex].text;
  });
}
