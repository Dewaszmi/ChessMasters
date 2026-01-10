function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");


async function createGroup() {
  const name = document.getElementById("group-name").value.trim();
  if (!name) return alert("Podaj nazwę grupy");

  const res = await fetch(window.AJAX_CREATE_GROUP_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ name }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    return alert("Błąd: " + (err.error || res.status));
  }


  window.location.reload();
}


async function assignStudent(studentId, btn) {
    const row = btn.closest("tr");
    const select = row.querySelector(".group-select");
    const groupId = select.value;
    const groupName = select.options[select.selectedIndex].text;

    if (!groupId) return alert("Wybierz grupę z listy!");

    try {
        const res = await fetch(window.AJAX_ASSIGN_STUDENT_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({ student_id: studentId, group_id: groupId }),
        });

        const data = await res.json();

        if (res.ok) {
            // Sukces: aktualizujemy tekst w kolumnie "Obecna Grupa"
            const currentGroupCell = row.querySelector(".current-group");
            currentGroupCell.innerHTML = `<span class="badge bg-info text-dark">${data.group_name}</span>`;
            alert("Przypisano studenta!");
            window.location.reload()
        } else {
            alert("Błąd: " + (data.error || "Nieznany błąd"));
        }
    } catch (error) {
        console.error("Błąd sieci:", error);
        alert("Błąd połączenia z serwerem.");
    }
}
